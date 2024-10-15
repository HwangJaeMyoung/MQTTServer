from django.test import TestCase
from .models import Location, Device,Sensor,Sensor_type,set_network,select,Sensor_value,Sensor_value_file, create_sensorValueFile
import json
import time
from .client import connect_mqtt,loop_mqtt

# Create your tests here.

class LocationModelTest(TestCase):
    def setUp(self):
        # 테스트할 객체를 생성
        Location.objects.create(name="Test Location1")
        Location.objects.create(name="Test Location2")
        Device.objects.create(name="Test Device1")
        Device.objects.create(name="Test Device2",attention= True)
        Sensor.objects.create(name="Test Sensor1",attention= True)
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
        sensor1.attached_device = device1
        sensor1.save()
        alist = ["Test Location1","Test Location2","Test Device2","Test Device1","Test Sensor1"]
        print(select("Test Device2"))
        # print(sensor)
        # connect_mqtt()
        # loop_mqtt()
        network = set_network("ICCMS/Test Location1/Test Location2/Test Device2/Test Device1/Test Sensor1/Register")
        print(network.run())
        print(device1.get_locations())

        fake_payload = json.dumps({
            "data": [{
                "time": "2000_5_1-1_1_1.122",
                "value":{"x":0,"y":1,"z":1}
            }
            ,{
                "time": "2000_5_1-1_1_2.122",
                "value":{"x":0,"y":1,"z":1}
            },
            {
                "time": "2000_5_1-1_1_3.122",
                "value":{"x":0,"y":1,"z":1}
            }
            ]
        }).encode("utf-8")
        received_msg = json.loads(fake_payload.decode("utf-8"))
        result = network.sensor.create_sensor_value(received_msg["data"])
        print(result)
        # print(network.sensor.sensor_value_set.all())
        print(Sensor_value.objects.all())
        create_sensorValueFile(network.sensor)
        print(Sensor_value.objects.all())
        # network.set_network_status(result)

        # result = sensor.create_sensor_value(received_msg["data"])        

        # self.assertEqual(location.name, "Test Location")