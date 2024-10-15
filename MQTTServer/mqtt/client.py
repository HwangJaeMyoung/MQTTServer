import paho.mqtt.client as mqtt
import json
from .topic import Sensor_topic
from .models import set_network
import time
import logging

logger = logging.getLogger("mqtt")

class ServerClient(mqtt.Client):
    BASE_TOPIC = "ICCMS/#"
    def __init__(self, callback_api_version: mqtt.CallbackAPIVersion = mqtt.CallbackAPIVersion.VERSION1, client_id: str | None = "", clean_session: bool | None = None, userdata: mqtt.Any = None, protocol: mqtt.MQTTProtocolVersion = mqtt.MQTTv311, transport: str = "tcp", reconnect_on_failure: bool = True, manual_ack: bool = False) -> None:
        super().__init__(callback_api_version, client_id, clean_session, userdata, protocol, transport, reconnect_on_failure, manual_ack)
        self.maintenance = False

    def on_connect(self,client, userdata, flags, rc):
        logger.info(f"mqtt connect")
        subscribe()

    def on_disconnect(self, client, userdata, v1_rc):
        logger.info(f"mqtt disconnect")
        if self.maintenance: return
        print(f"DisConnect. Reconnect in 5 seconds...")
        time.sleep(5)
        connect_mqtt()

    def on_message(self, client, userdata, msg):
        logger.debug(f"messsage arrive topic:{msg.topic}")
        network = set_network(msg.topic)
        if not network.run():
            logger.debug(f"messsage status is False topic:{msg.topic}")
            return False  
        if network.action_type == Sensor_topic.REGISTER:
            network.set_network_status(True)
            client.publish(network.confirm())
        elif network.action_type == Sensor_topic.CONFIRM: 
            network.set_network_status(True)

        elif network.action_type == Sensor_topic.VALUE:
            received_msg = json.loads(msg.payload.decode("utf-8"))
            received_data = received_msg["data"]
            result = network.sensor.create_sensor_value(received_data)
            network.set_network_status(result)
        else:
            logger.warning(f"sensor_networking_action_type is not defined {msg.topic}")
        
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
    mqtt_client.subscribe(ServerClient.BASE_TOPIC)

def start_maintenance():
    mqtt_client.activate_maintenance()
    mqtt_client.disconnect()

def end_maintenance():
    connect_mqtt()
    loop_mqtt()

def get_maintenance():
    return mqtt_client.maintenance
    


