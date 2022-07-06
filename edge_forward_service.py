import select
import socket
import threading
from io import BytesIO


class PacketDecoder:
    def __init__(self, sock, addr, callback):
        self.sock = sock
        self.addr = addr
        self.buffer = BytesIO()
        self.callback = callback

    def _report_packet(self):
        pack = self.buffer.getvalue()
        if not len(pack):
            return
        self.buffer = BytesIO()
        self.callback(self.addr, self.sock, pack)

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
    def __init__(self, server_sock, callback):
        self.server_sock = server_sock
        self.running = False
        self.socket_list = [server_sock]
        self.socket_table = {}
        self.decoder_table = {}
        self.callback = callback

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
        decoder = PacketDecoder(sock, addr, self.callback)
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


class ForwardService:
    def __init__(self, addr, packet_callback):
        self.addr = addr
        self.thread = None
        self.task = None
        self.packet_callback = packet_callback

    def _build_server_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.listen(10)

    def serve_forever(self):
        self._build_server_socket()
        self.task = ServiceTask(self.socket, self.packet_callback)
        self.thread = threading.Thread(target=self.task, name='accept')
        self.thread.start()

    def stop(self):
        self.task.stop()
        self.thread.stop()
        self.socket.close()
