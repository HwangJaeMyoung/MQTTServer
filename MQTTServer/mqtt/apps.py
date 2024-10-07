from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler


class MqttConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mqtt"
    def ready(self) -> None:
        from .client import connect_mqtt,loop_mqtt
        from .tasks import scheduled_task 
        connect_mqtt()
        loop_mqtt()
        scheduler = BackgroundScheduler()
        scheduler.add_job(scheduled_task, 'cron', minute='*/1')
        scheduler.start()
        return super().ready()
