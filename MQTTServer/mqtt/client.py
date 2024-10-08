import paho.mqtt.client as mqtt
import json
from .topic import REGISTER_TOPIC,SensorTopic
from .models import selectSensor,SensorValue,Sensor
import time
import logging

logging.basicConfig(filename='app.log',level=logging.DEBUG)

# 서버의 클라이언트 클래스
class ServerClient(mqtt.Client):
    def __init__(self, callback_api_version: mqtt.CallbackAPIVersion = mqtt.CallbackAPIVersion.VERSION1, client_id: str | None = "", clean_session: bool | None = None, userdata: mqtt.Any = None, protocol: mqtt.MQTTProtocolVersion = mqtt.MQTTv311, transport: str = "tcp", reconnect_on_failure: bool = True, manual_ack: bool = False) -> None:
        super().__init__(callback_api_version, client_id, clean_session, userdata, protocol, transport, reconnect_on_failure, manual_ack)
        self.maintenance = False

    def on_connect(self,client, userdata, flags, rc):
        subscribe()

    def on_disconnect(self, client, userdata, v1_rc):
        if self.maintenance: return
        print(f"DisConnect. Reconnect in 5 seconds...")
        time.sleep(5)
        connect_mqtt()

    def on_message(self, client, userdata, msg):
        receivedTopic = SensorTopic(msg.topic)
        sensor = selectSensor(receivedTopic.separate()[0])
        if not sensor: return
        if receivedTopic.isRegister():
            if not sensor.isOnline:return
            confirm_topic= receivedTopic.confirm()
            client.publish(confirm_topic.__str__())
            value_topic = confirm_topic.value()
            client.subscribe(value_topic.__str__())
            return
        else:
            received_msg = json.loads(msg.payload.decode("utf-8"))
            SensorValue.create_sensorValue(sensor,received_msg["data"])
            return
        
    def activate_maintenance(self):
        self.maintenance = True

    def deactivate_maintenance(self):
        self.maintenance = False
            
mqtt_client = ServerClient()
mqtt_client.enable_logger()

def connect_mqtt():
    broker_address = "localhost"
    broker_port = 1883
    while True:
        try:
            mqtt_client.connect(broker_address, broker_port, 60)  # 연결 시도
            print("Connected to MQTT broker")
            break 
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5) 

def loop_mqtt():
    mqtt_client.loop_start()

def subscribe():
    mqtt_client.subscribe(REGISTER_TOPIC.__str__())
    for sensor in Sensor.objects.filter(isOnline = True):
        sensor_name = sensor.getName()
        onlinedTopic=SensorTopic.init_from_sensor(sensor_name)
        value_topic = onlinedTopic.value()
        mqtt_client.subscribe(value_topic.__str__())

def start_maintenance():
    mqtt_client.activate_maintenance()
    mqtt_client.disconnect()


def end_maintenance():
    connect_mqtt()
    loop_mqtt()
    






