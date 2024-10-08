import paho.mqtt.client as mqtt
from typing import Literal
import json
from .topic import REGISTER_TOPIC,SensorTopic
from .models import Sensor,SensorValue
import datetime


# 서버의 클라이언트 클래스
class ServerClient(mqtt.Client):
    # def __init__(self, callback_api_version: mqtt.CallbackAPIVersion = mqtt.CallbackAPIVersion.VERSION2, client_id: str | None = "", clean_session: bool | None = None, userdata: mqtt.Any = None, protocol: mqtt.MQTTProtocolVersion = ..., transport: Literal['tcp'] | Literal['websockets'] | Literal['unix'] = "tcp", reconnect_on_failure: bool = True, manual_ack: bool = False) -> None:
    #     super().__init__(callback_api_version, client_id, clean_session, userdata, protocol, transport, reconnect_on_failure, manual_ack)
    def __init__(self, callback_api_version: mqtt.CallbackAPIVersion = mqtt.CallbackAPIVersion.VERSION1, client_id: str | None = "", clean_session: bool | None = None, userdata: mqtt.Any = None, protocol: mqtt.MQTTProtocolVersion = mqtt.MQTTv311, transport: str = "tcp", reconnect_on_failure: bool = True, manual_ack: bool = False) -> None:
        super().__init__(callback_api_version, client_id, clean_session, userdata, protocol, transport, reconnect_on_failure, manual_ack)
    
    def on_connect(self,client, userdata, flags, rc):
        client.subscribe(REGISTER_TOPIC.__str__())

        for sensor in Sensor.objects.filter(isOnline = True):
            sensor_name = sensor.getName()
            onlinedTopic=SensorTopic.init_from_sensor(sensor_name)
            value_topic = onlinedTopic.value()
            client.subscribe(value_topic.__str__())
            print(value_topic.__str__())

    def on_message(self, client, userdata, msg):
        receivedTopic = SensorTopic(msg.topic)
        sensor = Sensor.select(receivedTopic.separate()[0])
        if sensor == False:return
        if receivedTopic.isRegister():
            if not sensor.isOnline:return
            confirm_topic= receivedTopic.confirm()
            client.publish(confirm_topic.__str__(),1)

            value_topic = confirm_topic.value()
            client.subscribe(value_topic.__str__())
            return
        else:
            received_msg = json.loads(msg.payload.decode("utf-8"))
            SensorValue.create_sensorValue(sensor,received_msg["data"])
            return
            
if __name__ == "__main__":
    broker_address = "localhost"
    broker_port = 1883
    
    client =ServerClient()
    client.connect(broker_address, broker_port, 0)
    client.loop_start()

