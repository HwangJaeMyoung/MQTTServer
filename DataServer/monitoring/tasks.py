from .models import Plug ,Device,create_sensor_value_file,Sensor
import logging
import requests
from datetime import datetime, timedelta


logger = logging.getLogger("monitor")

def check_plug():
    logger.debug(f"excute check_plug()")
    plugs = Plug.objects.filter(attention = True).filter(target_status = True)
    for plug in plugs:
        result = plug.set_status()
        if result == False:
            logger.warning(f'Plug {plug.name} status is False.')
            continue
        result = plug.set_plug_status()
        if result == False:
            logger.warning(f'Failed to set plug status for {plug.name}.')
        else:
            logger.info(f'Successfully set plug status for {plug.name}.')

def check_device():
    devices = Device.objects.filter(attention = True).filter(target_status = True)
    for device in devices:        
        result = device.set_status()
        if not result:
            logger.warning(f'fail set plug status for {device.name}.')


def create_daily_file():
    sensors = Sensor.objects.filter(attention=True)
    yesterday = datetime.now() - timedelta(days=1)
    start_time = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)  # 어제 0시
    end_time = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    for sensor in sensors:
        create_sensor_value_file(sensor,start_time,end_time)
    return
