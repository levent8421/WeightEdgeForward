import json
import logging
import time

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from config import edgeServiceConfigObj


def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


host = edgeServiceConfigObj.mqtt_ip
rootCAPath = edgeServiceConfigObj.aws_root_ca_path
certificatePath = edgeServiceConfigObj.aws_certificate_path
privateKeyPath = edgeServiceConfigObj.aws_private_key_path
port = edgeServiceConfigObj.mqtt_port
useWebsocket = False
clientId = 'Test0001'
topic = 'forward'

logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

client = AWSIoTMQTTClient(clientId)
client.configureEndpoint(host, port)
client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
print('connect with:', clientId, host, port, rootCAPath, privateKeyPath, certificatePath)

client.configureAutoReconnectBackoffTime(1, 32, 20)
client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
client.configureDrainingFrequency(2)  # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec

client.connect()

client.subscribe(topic, 1, customCallback)
time.sleep(2)
loopCount = 0
while True:
    message = {'message': 'hallo', 'sequence': loopCount}
    messageJson = json.dumps(message)
    client.publish(topic, messageJson, 1)
    print('Published topic %s: %s\n' % (topic, messageJson))
    loopCount += 1
    time.sleep(1)
