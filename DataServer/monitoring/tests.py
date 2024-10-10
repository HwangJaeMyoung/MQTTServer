from django.test import TestCase
from .models import Location, Device,select_sensor,Sensor_networking,Sensor,Sensor_type,select_sensor_from_network
import json
import time

# Create your tests here.

class LocationModelTest(TestCase):
    def setUp(self):
        # 테스트할 객체를 생성
        Location.objects.create(name="Test Location1")
        Location.objects.create(name="Test Location2")
        Device.objects.create(name="Test Device1")
        Device.objects.create(name="Test Device2")
        Sensor.objects.create(name="Test Sensor1")
        Sensor_type.objects.create(name="Vibration")
        

    def test_location_creation(self):
        """Location 객체가 올바르게 생성되는지 확인"""
        location = Location.objects.get(name="Test Location1")
        location2 = Location.objects.get(name="Test Location2")
        device1  =  Device.objects.get(name="Test Device1")
        device2  =  Device.objects.get(name="Test Device2")
        sensor1  =  Sensor.objects.get(name="Test Sensor1")
        sensor_type1  =  Sensor_type.objects.get(name="Vibration")
        device1.location =location2
        device2.location =location2
        device1.parent = device2
        device1.save()
        device2.save()
        location2.parent = location
        location2.save()
        sensor1.sensor_type=sensor_type1
        sensor1.AttachedDevice = device1
        sensor1.save()
        alist = ["Test Location1","Test Location2","Test Device2","Test Device1","Test Sensor1"]
        print(select_sensor(alist))
        n=Sensor_networking(sensor = sensor, topic = "aa/aa/aa/aa/aa/aa")
        n.save()
        topic= "aa/aa/aa/aa/aa/aa"
        a= time.time()
        sensor= select_sensor(alist)
        b = time.time()
        select_sensor_from_network(topic)
        c = time.time()
        print(b-a)
        print(c-b)

        
        

        
        



        # fake_payload = json.dumps({
        #     "data": [{
        #         "time": "1999_1_1-1_1_1.1",
        #         "value":{"x":0,"y":1,"z":1}
        #     } for x in range(100)]
        # }).encode("utf-8")
        # received_msg = json.loads(fake_payload.decode("utf-8"))
        # print(received_msg["data"])
        
        
        # result = create_sensorValue(sensor1, received_msg["data"])        

        # self.assertEqual(location.name, "Test Location")