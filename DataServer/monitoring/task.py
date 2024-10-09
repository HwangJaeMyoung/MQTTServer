from PyP100 import PyP100
from .models import Plug ,Device
import logging

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
        result= device.set_status()

