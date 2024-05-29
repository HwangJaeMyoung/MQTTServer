from django.apps import AppConfig



class MqttConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mqtt"
    def ready(self) -> None:
        from .client import ServerClient
        global mqtt_client
        mqtt_client = ServerClient()
        
        broker_address = "localhost"
        broker_port = 1883

        mqtt_client.connect(broker_address, broker_port, 0)
        mqtt_client.loop_start()

        return super().ready()
