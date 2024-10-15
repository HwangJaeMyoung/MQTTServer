from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

class MonitoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitoring"
    
    def ready(self) -> None:
        from .tasks import check_plug
        # scheduler = BackgroundScheduler()
        # scheduler.add_job(check_plug, 'cron', second='*/1')
        # scheduler.start()
        return super().ready()