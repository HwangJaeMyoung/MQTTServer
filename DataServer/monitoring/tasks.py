from .models import Plug ,Device,create_sensor_value_file,Sensor,Sensor_value_file
import logging
import requests

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
        try:
            result= requests.get(f"http://{device.ip_address}",timeout=1)
            if result.status_code == 200:
                result =True
        except:
            result = False

        result= device.set_status()

        

def create_daily_file():
    sensors = Sensor.objects.filter(attention=True)
    for sensor in sensors:
        create_sensor_value_file(sensor)
    return
