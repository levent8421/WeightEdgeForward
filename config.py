class EdgeServiceConfig:
    def __init__(self):
        self.listen_ip = '0.0.0.0'
        self.listen_port = 8888
        self.mqtt_ip = 'a2w9j49tq4rytp-ats.iot.ap-southeast-2.amazonaws.com'
        self.mqtt_port = 8883
        self.mqtt_user = 'admin'
        self.mqtt_pwd = 'monolithiot'
        self.mqtt_forward_topic = 'sdk/test/Python'
        self.mqtt_subscribe_topic = 'sdk/test/Python'
        self.mqtt_qos = 1
        self.mqtt_client_id = 'basicPubSub'
        self.aws_root_ca_path = 'certs/root-CA.crt'
        self.aws_private_key_path = 'certs/scales.private.key'
        self.aws_certificate_path = 'certs/scales.cert.pem'


edgeServiceConfigObj = EdgeServiceConfig()
