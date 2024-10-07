from PyP100 import PyP100
from models import Plug ,Device

def check_plug():
    email = "DT.TUKOREA@gmail.com"  
    password = "DiK_WiMiS_30!"
    plugs = Plug.objects.filter(attention = True)
    for plug in plugs:
        try:
            p100 = PyP100.P100(str(plug.ip_address), email, password)
            p100.handshake() 
            p100.login() 
            plug_status = p100.getDeviceInfo()["device_on"]
            if plug.plug_status == plug_status:continue

            plug.plug_status = plug_status
            plug.save()
        except:
            plug.status= False
            plug.save()

def turn_off_plug():
    email = "DT.TUKOREA@gmail.com"  
    password = "DiK_WiMiS_30!"
    plugs = Plug.objects.filter(attention = True)
    for plug in plugs:
        try:
            p100 = PyP100.P100(str(plug.ip_address), email, password)
            p100.handshake() 
            p100.login() 
            p100.turnOff()
            plug.plug_status= False
            plug.save()
        except:
            plug.status= False
            plug.save()


def turn_on_plug():
    email = "DT.TUKOREA@gmail.com"  
    password = "DiK_WiMiS_30!"
    plugs = Plug.objects.filter(attention = True)
    for plug in plugs:
        try:
            p100 = PyP100.P100(str(plug.ip_address), email, password)
            p100.handshake() 
            p100.login() 
            p100.turnOn()
            plug.plug_status= True
            plug.save()
        except:
            plug.status= False
            plug.save()

def check_device():
    