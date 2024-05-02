from .client import ServerClient

# MQTT broker 정보
broker_address = "localhost"
broker_port = 1883

# MQTT 클라이언트 생성
client = ServerClient()

# MQTT 브로커에 연결
client.connect(broker_address, broker_port, 0)
client.loop_start()