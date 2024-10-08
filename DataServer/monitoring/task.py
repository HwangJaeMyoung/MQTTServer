from PyP100 import PyP100
from models import Plug ,Device

def check_plug():
    plugs = Plug.objects.filter(attention = True)
    for plug in plugs:
        plug.set_plug_status()



def check_device():
    pass