import paho.mqtt.client as mqtt
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from .models import Sensor,SensorValue,SensorValueFile
from MQTTServer.utils import VALUE_TYPE_LIST,SENSOR_TYPE_DICT,SENSOR_VALUE_MAP_DICT,MAX_VALUE_NUM
import struct
import pandas as pd
import csv
from io import StringIO 
from django.core.files.base import ContentFile
from django.utils import timezone

def checkSensor(topicList):
    result = False
    try:
        item = Sensor.objects.get(
            location= topicList[0],
            subLocation = topicList[1],
            part = topicList[2],
            sensorType = SENSOR_TYPE_DICT[topicList[3]],
            sensorIndex= int(topicList[4])
        )
        result = True
    except Sensor.DoesNotExist:
        print("error 1 : 잘못된 토픽 요청")
    except :
        print("error 0 : 예상치 못한 에러")
        print(f"topicList:{topicList}")
    return result

def getSensor(topicList):
    item = Sensor.objects.get(
        location= topicList[0],
        subLocation = topicList[1],
        part = topicList[2],
        sensorType = SENSOR_TYPE_DICT[topicList[3]],
        sensorIndex= int(topicList[4])
    )
    return item


# MQTT broker 정보
broker_address = "localhost"
broker_port = 1883

# MQTT 연결 콜백 함수
def on_connect(client, userdata, flags, rc):
    client.subscribe("ICCMS/+/+/+/+/+/Register")
    for sensor in Sensor.objects.filter(isOnline = True):
        for value in SENSOR_VALUE_MAP_DICT[SENSOR_TYPE_DICT[sensor.sensorType]]:
            client.subscribe(f"ICCMS/{sensor.location}/{sensor.subLocation}/{sensor.part}/{SENSOR_TYPE_DICT[sensor.sensorType]}/{sensor.sensorIndex}/{value}")

def on_message(client, userdata, msg):
    # 토픽에 따라 다른 작업 수행
    topicList = msg.topic.split("/")
    baseTopic  = "/".join(topicList[:-1])
    if topicList[-1] == "Register":
        if(checkSensor(topicList[1:-1])):
            sensor = getSensor(topicList[1:-1])
            if getSensor(topicList[1:-1]).isOnline:
                client.publish(f"{baseTopic}/Confirm",1,qos=1)
                for topic in SENSOR_VALUE_MAP_DICT[topicList[-3]]:
                    client.subscribe(f"{baseTopic}/{topic}",qos=1)

            else:
                sensor.isOnline = True
                sensor.save()
                client.publish(f"{baseTopic}/Confirm",1,qos=1)
                for topic in SENSOR_VALUE_MAP_DICT[topicList[-3]]:
                    client.subscribe(f"{baseTopic}/{topic}",qos=1)
            print(f"Register{topicList[2]}")

        else:
            client.publish(f"{baseTopic}/Comfirm",0,qos=1)

    elif topicList[-1] in VALUE_TYPE_LIST:
        try:
            sensor = getSensor(topicList[1:-1])
            messages = msg.payload.decode("utf-8")
            now = timezone.now()
            for i, type in  enumerate(SENSOR_VALUE_MAP_DICT[SENSOR_TYPE_DICT[sensor.sensorType]]):
                sensorValue = SensorValue(sensor=sensor,valueType=type,value=float(messages.split("_")[i]),time= now)
                sensorValue.save()
            
            for type in SENSOR_VALUE_MAP_DICT[SENSOR_TYPE_DICT[sensor.sensorType]]:
                if len(sensor.sensorvalue_set.filter(valueType=type)) >= MAX_VALUE_NUM or (sensor.time.day != sensorValue.time.day and len(sensor.sensorvalue_set.filter(valueType=type)) != 0 and sensor.time != None):
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

            sensor.time= sensorValue.time
            sensor.save()
        except:
            print("error 3 : 데이터 타입 오류")
        
 

    
# MQTT 클라이언트 생성
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

# MQTT 브로커에 연결
client.connect(broker_address, broker_port, 0)
client.loop_start()

# Django view 함수
@csrf_exempt
@require_POST  # POST 요청만 허용하도록 설정
def receive_mqtt(request):
    # MQTT 클라이언트 루프 실행
    client.loop_start()
    return HttpResponse("Receiving MQTT messages")

@require_GET  # GET 요청만 허용하도록 설정
def stop_receiving_mqtt(request):
    # MQTT 클라이언트 루프 중단
    client.loop_stop()
    return HttpResponse("Stopped receiving MQTT messages")