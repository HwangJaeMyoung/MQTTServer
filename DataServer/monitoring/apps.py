from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

class MonitoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitoring"
    
    def ready(self) -> None:
        from .tasks import check_plug,check_device,create_daily_file
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_plug, 'cron', second='*/1')
        # scheduler.add_job(check_device, 'cron', second='*/1')
        # scheduler.add_job(create_daily_file, 'cron', second='*/1')

        scheduler.start()
        return super().ready()