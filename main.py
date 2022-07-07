from action_handler import DataPacketHandler
from config import EdgeServiceConfigObj
from edge_forward_service import ForwardService
from mqtt_service import MqttService

mqtt = MqttService()
data_packet_handler = DataPacketHandler(mqtt)


def on_packet(addr, sock, data):
    data_packet_handler.handle_packet(addr, sock, data)


def on_mqtt_subscribe():
    print("订阅成功！")


def on_mqtt_message(msg, sock):
    addr = msg['addr']
    port = msg['port']
    packet = msg['packet']
    data_packet_handler.handle_packet((addr, port), sock, packet)


def main():
    service_addr = (EdgeServiceConfigObj.listen_ip, EdgeServiceConfigObj.listen_port)
    service = ForwardService(service_addr, on_packet)
    service.serve_forever()
    mqtt.mqtt_subscribe(topic="test", qos=1, msg_func=on_mqtt_message,
                        on_subscribe_func=on_mqtt_subscribe)


if __name__ == '__main__':
    main()
