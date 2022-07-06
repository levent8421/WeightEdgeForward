import configparser
import paho.mqtt.client as mqtt

from config import EdgeServiceConfigObj


class MqttService:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.host = EdgeServiceConfigObj.mqtt_ip
        self.port = EdgeServiceConfigObj.mqtt_port
        self.keepalive = 60
        self.name = EdgeServiceConfigObj.mqtt_name
        self.pwd = EdgeServiceConfigObj.mqtt_pwd
        self.mqtt_info = mqtt.Client(protocol=3)
        self.mqtt_info.username_pw_set(self.name, self.pwd)
        self.mqtt_info.connect(host=self.host, port=int(self.port), keepalive=int(self.keepalive))

    def mqtt_publish(self, topic=None, payload=None, qos=1):
        if topic is None or payload is None:
            return None
        self.mqtt_info.publish(topic=topic, payload=payload, qos=qos)

    def mqtt_subscribe(self, topic=None, qos=1, msg_func=None, on_subscribe_func=None):
        if topic is None:
            return None
        self.mqtt_info.subscribe(topic, qos)
        self.mqtt_info.on_message = msg_func
        self.mqtt_info.on_subscribe = on_subscribe_func
        self.mqtt_info.loop_forever()
