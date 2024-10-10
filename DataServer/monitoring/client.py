import paho.mqtt.client as mqtt
import json
from .topic import REGISTER_TOPIC,Sensor_topic
from .models import select_sensor,SensorValue,Sensor, select_network,Sensor_networking
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
        # topic: ICCMS/A/A/B/B/C
        network= select_network(msg.topic)
        # 존재했던 토픽인지 확인-> 아니었다면 센서 찾고 찾았다면 토픽의 동작 확인하고 그것을 network에 추가하고 해당 토픽에 대한 기록 작성, 해당 토픽에 대한 시간 최신화
        ## 부착된 센서에 대해서 일정시간 업데이트가 없는지 모니터링 필요 
        # 센서의 어텐션 상태를 확인 
        # 동작에 따른 동작 실시 
        if not network:
            receivedTopic = Sensor_topic(msg.topic)
            sensor = select_sensor(receivedTopic.separate()[0])

            if not sensor:
                Sensor_networking.objects.create(topic= msg.topic,status=False,action_type = receivedTopic.action_type)
                return 
            elif not receivedTopic.action_type in receivedTopic.ACTION_TYPE:
                Sensor_networking.objects.create(sensor =sensor, topic= msg.topic,status=False,action_type = receivedTopic.action_type)
                return 
            
            network = Sensor_networking(sensor =sensor, topic= msg.topic,action_type = receivedTopic.action_type,status= True)
            network.save()
        
        sensor = network.sensor
        
        if not sensor.attention: return False
        if not sensor.AttachedDevice.attention: return False
        if not sensor.CollectingDevice.attention: return False

        if network.action_type == Sensor_topic.REGISTER:
            try:
                confirm_network = sensor.sensor_networking_set.get(action_type=Sensor_topic.REGISTER)
                client.publish(confirm_network.topic)
            except Sensor_networking.DoesNotExist:
                confirm_topic= receivedTopic.confirm()
                client.publish(confirm_topic.__str__())

            value_topic = confirm_topic.value()
            client.subscribe(value_topic.__str__())

        elif network.action_type == Sensor_topic.VALUE:
            received_msg = json.loads(msg.payload.decode("utf-8"))
            SensorValue.create_sensorValue(sensor,received_msg["data"])
        else:
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
        onlinedTopic=Sensor_topic.init_from_sensor(sensor_name)
        value_topic = onlinedTopic.value()
        mqtt_client.subscribe(value_topic.__str__())

def start_maintenance():
    mqtt_client.activate_maintenance()
    mqtt_client.disconnect()


def end_maintenance():
    connect_mqtt()
    loop_mqtt()
    






