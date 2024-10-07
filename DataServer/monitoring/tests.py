from django.test import TestCase

# Create your tests here.


email = "DT.TUKOREA@gmail.com"  
password = "DiK_WiMiS_30!"  
p100 = PyP100.P100(str(self.ip_address), email, password)
p100.handshake()  
p100.login() 
p100.turnOff()
self.plug_status = False
self.save()


def check_plug():
    email = "DT.TUKOREA@gmail.com"  
    password = "DiK_WiMiS_30!"
    p100 = PyP100.P100(str(self.ip_address), email, password)
    p100.handshake()  
    p100.login() 
    p100.turnOff()
    self.plug_status = False
    self.save()
