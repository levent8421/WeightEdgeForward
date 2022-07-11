import json


class ActionHandler:
    def handle_action(self, addr, sock, packet):
        pass


class ForwardMQTTMessage:
    def __init__(self):
        self.source_ip = None
        self.source_port = None
        self.message_type = None
        self.packet = None

    def as_mqtt_message(self):
        res = {
            'type': self.message_type,
            'sourceIp': self.source_ip,
            'sourcePort': self.source_port,
            'packet': self.packet
        }
        return json.dumps(res)


class CommonsMQTTForwardActionHandler(ActionHandler):
    def __init__(self, mqtt_client):
        self.client = mqtt_client

    def handle_action(self, addr, sock, packet):
        msg = ForwardMQTTMessage()
        msg.source_ip = addr[0]
        msg.source_port = addr[1]
        msg.message_type = packet['type']
        msg.packet = packet
        mqtt_msg = msg.as_mqtt_message()
        self.client.forward(mqtt_msg)
        return {
            'code': 200,
            'msg': 'MQTT_FORWARDED'
        }


class HeartbeatActionHandler(CommonsMQTTForwardActionHandler):
    def __init__(self, mqtt_client, service):
        super().__init__(mqtt_client)
        self.service = service

    def handle_action(self, addr, sock, packet):
        app_name = packet['data']['appName']
        self.service.add_socket_relation(app_name, sock)
        return super().handle_action(addr, sock, packet)
