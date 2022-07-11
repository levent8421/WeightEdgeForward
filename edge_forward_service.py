import json
import select
import socket
import threading
from io import BytesIO

from config import edgeServiceConfigObj


class ForwardException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DataPacketHandler:
    def __init__(self, response_callback):
        self.handler_table = {}
        self.response_callback = response_callback

    def get_handler(self, action, version):
        if action in self.handler_table:
            handlers = self.handler_table[action]
            if version in handlers:
                return handlers[version]
        return None

    def _handler_request(self, addr, sock, packet):
        action = packet['action']
        action_version = packet['actionVersion']
        handler = self.get_handler(action, action_version)
        if not handler:
            resp_data = {
                'code': 404,
                'msg': f'can not find action:{action}'
            }
        else:
            resp_data = handler.handle_action(addr, sock, packet)
        dest_logical_name = packet['sourceLogicalName']
        dest_physical_addr = packet['sourcePhysicalAddr']
        source_logical_name = packet['destLogicalName']
        source_physical_addr = packet['sourcePhysicalAddr']
        trace_id = packet['traceId']
        seq_no = packet['seqNo']
        resp = {
            "action": action,
            "actionVersion": action_version,
            "data": resp_data,
            "destLogicalName": dest_logical_name,
            "destPhysicalAddr": dest_physical_addr,
            "priority": 3,
            "seqNo": seq_no,
            "sourceLogicalName": source_logical_name,
            "sourcePhysicalAddr": source_physical_addr,
            "traceId": trace_id,
            "traceName": f'Response:{action}',
            "type": "response"
        }
        resp_json = json.dumps(resp)
        sock.send(b'\x02')
        sock.send(resp_json.encode())
        sock.send(b'\x03')

    def handle_packet(self, addr, sock, packet):
        packet_obj = json.loads(packet)
        action = packet_obj['action']
        action_version = packet_obj['actionVersion']
        seq_no = packet_obj['seqNo']
        packet_type = packet_obj['type']
        print(f'{packet_type} from [{addr}]:{action},{action_version},{seq_no}')
        if packet_type == 'request':
            self._handler_request(addr, sock, packet_obj)
        elif packet_type == 'response':
            self.response_callback and self.response_callback(addr, sock, packet_obj)
        else:
            print('Bad packet type:', packet_type)

    def add_request_handler(self, action_name, action_version, handler):
        if action_name not in self.handler_table:
            self.handler_table[action_name] = {}
        handlers = self.handler_table[action_name]
        handlers[action_version] = handler


class PacketDecoder:
    def __init__(self, sock, addr, handler):
        self.sock = sock
        self.addr = addr
        self.buffer = BytesIO()
        self.handler = handler

    def _report_packet(self):
        pack = self.buffer.getvalue()
        if not len(pack):
            return
        self.buffer = BytesIO()
        self.handler.handle_packet(self.addr, self.sock, pack)

    def push_date(self, data):
        data_size = len(data)
        i = 0
        cursor = 0
        while i < data_size:
            byte = data[i]
            if byte == 0x02 or byte == 0x03:
                data_slice = data[cursor + 1: i]
                self.buffer.write(data_slice)
                self._report_packet()
                cursor = i
            i += 1


SELECT_INTERVAL = 1


class ServiceTask:
    def __init__(self, server_sock, handler):
        self.server_sock = server_sock
        self.running = False
        self.socket_list = [server_sock]
        self.socket_table = {}
        self.decoder_table = {}
        self.handler = handler
        self.sock_relation_table = {}

    def __call__(self, *args, **kwargs):
        self.running = True
        while self.running:
            r_list, w_list, e_list = select.select(self.socket_list, [], self.socket_list, SELECT_INTERVAL)
            if len(r_list):
                self.handle_connection_event(r_list)
            if len(e_list):
                self.handle_connection_errors(e_list)

    def _get_decoder(self, sock):
        if sock in self.decoder_table:
            return self.decoder_table[sock]
        addr = self._get_socket_addr(sock)
        decoder = PacketDecoder(sock, addr, self.handler)
        self.decoder_table[sock] = decoder
        return decoder

    def _listen_socket(self, sock, addr):
        self.socket_list.append(sock)
        self.socket_table[sock] = addr

    def _remove_socket(self, sock):
        self.socket_list.remove(sock)
        return self.socket_table.pop(sock)

    def _get_socket_addr(self, sock):
        if sock in self.socket_table:
            return self.socket_table[sock]
        return None

    def _read_socket_data(self, sock, data):
        addr = self._get_socket_addr(sock)
        if not addr:
            print('Unexpected socket:', sock)
            return
        decoder = self._get_decoder(sock)
        decoder.push_date(data)

    def handle_connection_event(self, sock_list):
        for sock in sock_list:
            if sock == self.server_sock:
                sock, addr = sock.accept()
                print(f'Connection from:{addr}')
                self._listen_socket(sock, addr)
            else:
                data = sock.recv(1024)
                if not len(data):
                    # socket closed
                    addr = self._remove_socket(sock)
                    print('socket closed: ', addr)
                else:
                    # socket data
                    self._read_socket_data(sock, data)

    def handle_connection_errors(self, sock_list):
        for sock in sock_list:
            print('error:', sock)
            self._remove_socket(sock)

    def stop(self):
        self.running = False

    def find_socket_by_app_name(self, app_name):
        if app_name in self.sock_relation_table:
            return self.sock_relation_table[app_name]
        return None

    def add_socket_relation(self, app_name, sock):
        self.sock_relation_table[app_name] = sock

    def get_sock_addr(self, sock):
        if sock in self.socket_table:
            return self.socket_table[sock]
        return None


class ForwardService:
    def __init__(self, addr, packet_handler):
        self.addr = addr
        self.thread = None
        self.task = None
        self.packet_handler = packet_handler

    def _build_server_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.listen(10)

    def serve_forever(self):
        self._build_server_socket()
        self.task = ServiceTask(self.socket, self.packet_handler)
        self.thread = threading.Thread(target=self.task, name='accept')
        self.thread.start()

    def stop(self):
        self.task.stop()
        self.thread.stop()
        self.socket.close()

    def send(self, app_name, packet):
        sock = self.task.find_socket_by_app_name(app_name)
        if not sock:
            raise ForwardException(f'Can not find connection:{app_name}')
        addr = self.task.get_sock_addr(sock)
        packet['destLogicalName'] = 'SCADA_WSA'
        packet['destPhysicalAddr'] = f'{addr[0]}:{addr[1]}'
        packet['sourceLogicalName'] = 'FORWARD_SERVICE'
        packet['sourcePhysicalAddr'] = f'{edgeServiceConfigObj.listen_ip}:{edgeServiceConfigObj.listen_port}'
        json_body = json.dumps(packet).encode()
        sock.send(b'\x02')
        sock.send(json_body)
        sock.send(b'\x03')

    def add_socket_relation(self, app_name, sock):
        self.task.add_socket_relation(app_name, sock)
