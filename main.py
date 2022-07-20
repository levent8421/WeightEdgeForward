import json

from action_handler import CommonsMQTTForwardActionHandler, HeartbeatActionHandler
from awsiot import MQTTClient
from config import edgeServiceConfigObj
from edge_forward_service import ForwardService, DataPacketHandler

DEFAULT_ACTION_VERSION = 'V0.1'


def response_packet_handler(mqtt_client):
    handler = CommonsMQTTForwardActionHandler(mqtt_client)

    def callback(addr, sock, pack):
        handler.handle_action(addr, sock, pack)

    return callback


def init_action_handlers(packet_handler, mqtt_client, service):
    actions = {
        "notify.heartbeat": HeartbeatActionHandler(mqtt_client, service),
        "notify.startup": CommonsMQTTForwardActionHandler(mqtt_client),
        "ruok.get": CommonsMQTTForwardActionHandler(mqtt_client),
        "balance.no.set": CommonsMQTTForwardActionHandler(mqtt_client),
        "balance.sku.set": CommonsMQTTForwardActionHandler(mqtt_client),
        "notify.th_sensor.window_records": CommonsMQTTForwardActionHandler(mqtt_client),
        "th_sensor.set_params": CommonsMQTTForwardActionHandler(mqtt_client),
        "notify.th_sensor.status": CommonsMQTTForwardActionHandler(mqtt_client),
        "notify.balance.state": CommonsMQTTForwardActionHandler(mqtt_client),
        "notify.balance.weight_changed": CommonsMQTTForwardActionHandler(mqtt_client),
        "balance.data.get": CommonsMQTTForwardActionHandler(mqtt_client),
        "balance.groups.get": CommonsMQTTForwardActionHandler(mqtt_client),
        "notify.balance.merged": CommonsMQTTForwardActionHandler(mqtt_client),
        "notify.balance.unmerged": CommonsMQTTForwardActionHandler(mqtt_client),
        "thsensor.data.get": CommonsMQTTForwardActionHandler(mqtt_client),
        "notify.th_sensor.point_records": CommonsMQTTForwardActionHandler(mqtt_client),
        "balance.valid.set": CommonsMQTTForwardActionHandler(mqtt_client),
        "th_sensor.eoable_set": CommonsMQTTForwardActionHandler(mqtt_client),
    }
    for action in actions.keys():
        packet_handler.add_request_handler(action, DEFAULT_ACTION_VERSION, actions[action])


def read_prop(props, name):
    if name in props:
        return props[name]
    return None


def on_mqtt_msg(service):
    def callback(topic, payload):
        print(f'MQTT_MSG[{topic}]:{payload}')
        payload = json.loads(payload.decode())
        app_name = read_prop(payload, 'appName')
        data = read_prop(payload, 'data')
        seq_no = read_prop(payload, 'seqNo')
        action = read_prop(payload, 'action')
        action_version = read_prop(payload, 'actionVersion')
        packet = {
            'action': action,
            'actionVersion': action_version,
            'data': data,
            'priority': 3,
            'seqNo': seq_no,
            'traceId': seq_no,
            "traceName": topic,
            "type": "request"
        }
        try:
            service.send(app_name, packet)
        except Exception as e:
            print(f'Error on send:', repr(e))

    return callback


def main():
    packet_handler = DataPacketHandler(None)

    server_addr = (edgeServiceConfigObj.listen_ip, edgeServiceConfigObj.listen_port)
    forward_service = ForwardService(server_addr, packet_handler)
    forward_service.serve_forever()

    mqtt_client = MQTTClient(on_mqtt_msg(forward_service))
    init_action_handlers(packet_handler, mqtt_client, forward_service)
    mqtt_client.connect()
    packet_handler.response_callback = response_packet_handler(mqtt_client)


if __name__ == '__main__':
    main()
