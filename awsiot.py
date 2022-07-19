from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from config import edgeServiceConfigObj


def _gen_callback(callback):
    def callback_wrapper(client, user_data, msg):
        topic = msg.topic
        payload = msg.payload
        callback(topic, payload)

    return callback_wrapper


class MQTTClient:
    def __init__(self, msg_callback):
        self.msg_callback = msg_callback
        self.client = None

    def connect(self):
        self._build_client()
        self.client.connect()
        self.client.subscribe(edgeServiceConfigObj.mqtt_subscribe_topic, edgeServiceConfigObj.mqtt_qos,
                              _gen_callback(self.msg_callback))

    def _build_client(self):
        host = edgeServiceConfigObj.mqtt_ip
        port = edgeServiceConfigObj.mqtt_port
        self.client = AWSIoTMQTTClient(edgeServiceConfigObj.mqtt_client_id)
        self.client.configureEndpoint(host, port)
        self.client.configureCredentials(edgeServiceConfigObj.aws_root_ca_path,
                                         edgeServiceConfigObj.aws_private_key_path,
                                         edgeServiceConfigObj.aws_certificate_path)
        self.client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec

    def forward(self, msg):
        if not self.client:
            print('IGNORE:', msg)
            return
        self.client.publish(edgeServiceConfigObj.mqtt_forward_topic, msg, edgeServiceConfigObj.mqtt_qos)
