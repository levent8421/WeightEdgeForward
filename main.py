from action_handler import DataPacketHandler
from config import EdgeServiceConfigObj
from edge_forward_service import ForwardService

data_packet_handler = DataPacketHandler()


def on_packet(addr, sock, data):
    data_packet_handler.handle_packet(addr, sock, data)


def main():
    service_addr = (EdgeServiceConfigObj.listen_ip, EdgeServiceConfigObj.listen_port)
    service = ForwardService(service_addr, on_packet)
    service.serve_forever()


if __name__ == '__main__':
    main()
