import paho.mqtt.client as mqtt
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from .models import Sensor,SensorValue
from MQTTServer.utils import VALUE_TYPE_LIST,SENSOR_TYPE_DICT,SENSOR_VALUE_MAP_DICT 

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

def on_message(client, userdata, msg):
    # 토픽에 따라 다른 작업 수행
    topicList = msg.topic.split("/")
    baseTopic  = "/".join(topicList[:-1]) 
    if topicList[-1] == "Register":
        if(checkSensor(topicList[1:-1])):
            sensor = getSensor(topicList[1:-1])
            if getSensor(topicList[1:-1]).isOnline:
                pass
            else:
                sensor.isOnline = True
                sensor.save()
                client.publish(f"{baseTopic}/Comfirm",1,qos=1)
                for topic in SENSOR_VALUE_MAP_DICT[topicList[-3]]:
                    client.subscribe(f"{baseTopic}/{topic}")
        else:
            client.publish(f"{baseTopic}/Comfirm",0,qos=1)

    elif topicList[-1] in VALUE_TYPE_LIST:
        try:
            sensor = getSensor(topicList[1:-1])
            value = SensorValue(sensor=sensor,valueType=topicList[-1],value=float(msg.payload.decode("utf-8")))
            value.save()
        except:
            print("error 3 : 데이터 타입 오류")
            
# MQTT 클라이언트 생성
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# MQTT 브로커에 연결
client.connect(broker_address, broker_port, 60)
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