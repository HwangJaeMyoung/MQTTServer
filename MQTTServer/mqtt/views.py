from .client import ServerClient


# MQTT broker 정보
broker_address = "localhost"
broker_port = 1883

# MQTT 클라이언트 생성
client = ServerClient()

# MQTT 브로커에 연결

# if not isinstance(client._protocol, str) or not client._protocol.isdigit():
#     client._protocol = "3" 
# client.protocol_version = 3

client.connect(broker_address, broker_port, 60)
client.loop_start()
