import paho.mqtt.client as mqtt
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from models import Sensor

TOPIC_TOTAL_LEVEL = 7
REGISTER = 1
VALUE= 2
VALUE_TYPE_LIST = ["X","Y","Z","Temperature","Humidity","Current"]

def checkSensor(topicList):
    ""
    result = True
    try:
        new_value = Sensor ##/찾고
    except:
        result =False
    
    return result

def checkTopic(topicList):
    result = False
    if len(topicList) == TOPIC_TOTAL_LEVEL:
        if checkSensor(topicList[0:-1]):
            if topicList[-1] == "Register":         
                result = REGISTER
            elif topicList[-1] in VALUE_TYPE_LIST:
                result = VALUE
    return result


# MQTT broker 정보
broker_address = "localhost"
broker_port = 1883


# MQTT 연결 콜백 함수
def on_connect(client, userdata, flags, rc):
    client.subscribe("ICCMS/#")

def on_message(client, userdata, msg):
    # 토픽에 따라 다른 작업 수행
    print("topic:",msg.topic)
    topicList = msg.topic.split("/")
    result =checkTopic(topicList)
    if result:
        if result == REGISTER:
            print("등록")
            client.publish("/".join(topicList[:-1]) + "/Confirm","11",qos=1)
        elif result == VALUE:
            print("데이터")
    print("Received message:", msg.payload.decode("utf-8"))


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