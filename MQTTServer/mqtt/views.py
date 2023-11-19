import paho.mqtt.client as mqtt
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET

# MQTT broker 정보
broker_address = "localhost"
broker_port = 1883

# MQTT 연결 콜백 함수
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("locationA/typeA/id")
    client.subscribe("locationB/typeB/id")
    client.subscribe("locationC/typeC/id")

def on_message(client, userdata, msg):
    # 토픽에 따라 다른 작업 수행
    print("topic:",msg.topic)
    tmp = msg.topic.split("/")
    print(f"location:{tmp[0]}\ntype:{tmp[1]}\nid:{tmp[2]}")
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