from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler


class MqttConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mqtt"
    def ready(self) -> None:
        from .client import connect_mqtt,loop_mqtt
        connect_mqtt()
        loop_mqtt()
        return super().ready()
