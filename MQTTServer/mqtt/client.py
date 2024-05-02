import paho.mqtt.client as mqtt
from typing import Literal
from django.utils import timezone
import csv
from io import StringIO 


from .topic import REGISTER_TOPIC,SensorTopic
from .models import Sensor,SensorValue

 
if __name__ == "__main__":
    pass

# MQTT broker 정보
broker_address = "localhost"
broker_port = 1883

# 서버의 클라이언트 클래스
class ServerClient(mqtt.Client):
    def __init__(self, callback_api_version: mqtt.CallbackAPIVersion = mqtt.CallbackAPIVersion.VERSION1, client_id: str | None = "", clean_session: bool | None = None, userdata: mqtt.Any = None, protocol: mqtt.MQTTProtocolVersion = ..., transport: Literal['tcp'] | Literal['websockets'] | Literal['unix'] = "tcp", reconnect_on_failure: bool = True, manual_ack: bool = False) -> None:
        super().__init__(callback_api_version, client_id, clean_session, userdata, protocol, transport, reconnect_on_failure, manual_ack)
    
    def on_connect(client, userdata, flags, rc):
        client.subscribe(REGISTER_TOPIC)

        # 이미 수신 가능인 얘들 열기
        for sensor in Sensor.objects.filter(isOnline = True):
            sensor_data = sensor.getData()
            onlinedTopic=SensorTopic.init_from_list(sensor_data)
            for collect_topic in onlinedTopic.collect():
                client.subscribe(collect_topic,qos=1)
    def on_message(client, userdata, msg):
        receivedTopic = SensorTopic(msg.topic)
        sensor = Sensor.select(receivedTopic.separate()[0])
        if sensor == False:return
        if receivedTopic.isRegister():
            if not sensor.isOnline:return
            confirm_topic= receivedTopic.confirm()
            client.publish(confirm_topic,1,qos=1)
            for collect_topic in receivedTopic.collect():
                client.subscribe(collect_topic,qos=1)
        else:
            received_msg = msg.payload.decode("utf-8")
            now = timezone.now()
            try:
                received_value = received_msg.split("_")
                for i, type in enumerate(sensor.getValueType()):
                    sensorValue = SensorValue(sensor=sensor,valueType=type,value=float(received_value[i]),time= now) 
                    sensorValue.save()
                sensor.time= sensorValue.time
                sensor.save()
                
                for type in sensor.getValueType():
                    if len(sensor.sensorvalue_set.filter(valueType=type)) == 0: continue
                    if len(sensor.sensorvalue_set.filter(valueType=type)) < Sensor.MAX_VALUE_NUM and (sensor.time.day == sensorValue.time.day): continue
                    data_list = sensor.sensorvalue_set.filter(valueType=type).order_by("time").values_list("time","value")
                    csv_data = StringIO()
                    csv_data.write(u'\ufeff')
                    writer = csv.writer(csv_data)
                    writer.writerow(["",'Time_[s]', "Acceleration[g]"])
                    
                    for i, value in enumerate(data_list):
                        time = (value[0] - data_list[0][0]).seconds
                        writer.writerow([i,time,value[1]])

                    file_content = csv_data.getvalue().encode("utf-8")
                    sensorValueFile= SensorValueFile(sensor=sensor,valueType=type,time= data_list[0][0])
                    
                    sensorValueFile.file.save(
                        f'{sensor.location}_{sensor.subLocation}_{sensor.part}_{SENSOR_TYPE_DICT[sensor.sensorType]}_{sensor.sensorIndex}/{data_list[0][0].year}_{data_list[0][0].month}_{data_list[0][0].day}_raw_{type}/{data_list[0][0].year}_{data_list[0][0].month}_{data_list[0][0].day}-{data_list[0][0].hour}_{data_list[0][0].minute}_{data_list[0][0].second}_timeraw_{type.lower()}.csv',
                        ContentFile(file_content))
                    sensorValueFile.save()
                    for value in sensor.sensorvalue_set.filter(valueType=type):
                        value.delete()


            except:
                print("error 3 : 데이터 타입 오류")
            
        # elif topicList[-1] in VALUE_TYPE_LIST:
        #     try:
        #         sensor = getSensor(topicList[1:-1])
        #         messages = msg.payload.decode("utf-8")
        #         now = timezone.now()

        #         for i, type in  enumerate(SENSOR_VALUE_MAP_DICT[SENSOR_TYPE_DICT[sensor.sensorType]]):
        #             # sensorValue = SensorValue(sensor=sensor,valueType=type,value=float(msg.payload.decode("utf-8"))) # 수정해야함
        #             sensorValue = SensorValue(sensor=sensor,valueType=type,value=float(messages.split("_")[i]),time= now) # 수정해야함
        #             sensorValue.save()
                
        #         for type in SENSOR_VALUE_MAP_DICT[SENSOR_TYPE_DICT[sensor.sensorType]]:
        #             if len(sensor.sensorvalue_set.filter(valueType=type)) >= MAX_VALUE_NUM or (sensor.time.day != sensorValue.time.day and len(sensor.sensorvalue_set.filter(valueType=type)) != 0 and sensor.time != None):

        #                 data_list = sensor.sensorvalue_set.filter(valueType=type).order_by("time").values_list("time","value")
        #                 csv_data = StringIO()
        #                 csv_data.write(u'\ufeff')
        #                 writer = csv.writer(csv_data)
        #                 writer.writerow(["",'Time_[s]', "Acceleration[g]"])
                        
        #                 for i, value in enumerate(data_list):
        #                     time = (value[0] - data_list[0][0]).seconds
        #                     writer.writerow([i,time,value[1]])

        #                 file_content = csv_data.getvalue().encode("utf-8")
        #                 sensorValueFile= SensorValueFile(sensor=sensor,valueType=type,time= data_list[0][0])
                        
        #                 sensorValueFile.file.save(
        #                     f'{sensor.location}_{sensor.subLocation}_{sensor.part}_{SENSOR_TYPE_DICT[sensor.sensorType]}_{sensor.sensorIndex}/{data_list[0][0].year}_{data_list[0][0].month}_{data_list[0][0].day}_raw_{type}/{data_list[0][0].year}_{data_list[0][0].month}_{data_list[0][0].day}-{data_list[0][0].hour}_{data_list[0][0].minute}_{data_list[0][0].second}_timeraw_{type.lower()}.csv',
        #                     ContentFile(file_content))
        #                 sensorValueFile.save()
        #                 for value in sensor.sensorvalue_set.filter(valueType=type):
        #                     value.delete()

        #         sensor.time= sensorValue.time
        #         sensor.save()
        #     except:
        #         print("error 3 : 데이터 타입 오류")

# MQTT 브로커에 연결
client.connect(broker_address, broker_port, 0)
client.loop_start()
