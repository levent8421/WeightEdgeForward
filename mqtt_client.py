from threading import Thread

from paho.mqtt.client import Client as PahoMQTTClient

from config import edgeServiceConfigObj


class MQTTConnectCallback:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        print('connect', args, kwargs)


class MQTTClient:
    def __init__(self, msg_callback):
        self.cli = None
        self.looper = None
        self.msg_callback = msg_callback

    def connect(self):
        self.disconnect()
        self.cli = PahoMQTTClient(self._get_client_id())
        self.cli.username_pw_set(edgeServiceConfigObj.mqtt_user, edgeServiceConfigObj.mqtt_pwd)
        connect_callback = MQTTConnectCallback()
        self.cli.on_connect = connect_callback
        self.cli.on_message = self._handle_msg()
        print(f'connecting MQTTBroker with ({edgeServiceConfigObj.mqtt_ip},{edgeServiceConfigObj.mqtt_port})......')
        self.cli.connect(edgeServiceConfigObj.mqtt_ip, edgeServiceConfigObj.mqtt_port)
        print(f'Subscribe[{edgeServiceConfigObj.mqtt_subscribe_topic}]')
        self.cli.subscribe(edgeServiceConfigObj.mqtt_subscribe_topic)
        self.cli.loop_start()
        print('MQTT Connected!')

    def _start_looper(self):
        def loop_task():
            pass

        self.looper = Thread(target=loop_task)
        self.looper.start()

    def disconnect(self):
        if not self.looper:
            return
        self.looper.stop()
        self.cli.disconnect()

    def _handle_msg(self):
        def callback(client, user_data, msg):
            self.msg_callback and self.msg_callback(msg.topic, msg.payload)

        return callback

    @staticmethod
    def _get_client_id():
        return 'PYTHON_MQTT_CLIENT_1'

    def forward(self, msg):
        if not self.cli:
            print('IGNORE:', msg)
            return
        self.cli.publish(topic=edgeServiceConfigObj.mqtt_forward_topic, payload=msg, qos=edgeServiceConfigObj.mqtt_qos)
