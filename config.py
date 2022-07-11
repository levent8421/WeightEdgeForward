class EdgeServiceConfig:
    def __init__(self):
        self.listen_ip = '0.0.0.0'
        self.listen_port = 8888
        self.mqtt_ip = '192.168.233.100'
        self.mqtt_port = 1883
        self.mqtt_user = 'admin'
        self.mqtt_pwd = 'monolithiot'
        self.mqtt_forward_topic = 'weight_msg_forward'
        self.mqtt_subscribe_topic = 'weight_msg_subscribe'
        self.mqtt_qos = 1


edgeServiceConfigObj = EdgeServiceConfig()
