import json


class ActionHandler:
    def handle_action(self, addr, sock, packet):
        return {
            'code': 200
        }


class StartupActionHandler(ActionHandler):
    def handle_action(self, addr, sock, packet):
        return {
            'code': 200
        }


class HeartbeatActionHandler(ActionHandler):
    def handle_action(self, addr, sock, packet):
        return {
            'code': 200
        }


class DataPacketHandler:
    def __init__(self, mqtt):
        self.mqtt = mqtt
        self.handler_table = {
            'notify.startup': StartupActionHandler(),
            'notify.heartbeat': HeartbeatActionHandler(),
        }

    def get_handler(self, action):
        if action in self.handler_table:
            return self.handler_table[action]
        return None

    def handler_request(self, addr, sock, packet):
        action = packet['action']
        action_version = packet['actionVersion']
        handler = self.get_handler(action)
        self.send_mqtt(addr, packet)
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

    def handler_response(self, addr, sock, packet):
        action = packet['action']
        action_version = packet['actionVersion']
        handler = self.get_handler(action)
        self.send_mqtt(addr, packet)
        if not handler:
            resp_data = {
                'code': 404,
                'msg': f'can not find action:{action}'
            }
        else:
            resp_data = handler.handle_action(addr, sock, packet)

    def handle_packet(self, addr, sock, packet):
        packet_obj = json.loads(packet)
        action = packet_obj['action']
        action_version = packet_obj['actionVersion']
        seq_no = packet_obj['seqNo']
        packet_type = packet_obj['type']
        print(packet_type, seq_no, action, action_version)
        if packet_type == 'request':
            self.handler_request(addr, sock, packet_obj)
        elif packet_type == 'response':
            self.handler_response(addr, sock, packet_obj)
        else:
            print('Bad packet type:', packet_type)

    def send_mqtt(self, addr, packet):
        param = {
            "addr": addr[0],
            "port": addr[1],
            "packet": packet
        }
        self.mqtt.mqtt_publish(topic="test", payload=json.dumps(param))
