from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime
from enum import Enum
import csv
from io import StringIO 
from PyP100 import PyP100
from django.db.models import UniqueConstraint

class Sensor(models.Model):
    MAX_VALUE_NUM = 4096
    class SensorType(Enum):
        Vibration = 0
        Temperature = 1
        Humidity = 2
        TemperatureHumidity = 3
        Current = 4
    SENSOR_TYPE_VALUES = {
        "Vibration" :["x","y","z"],
        "Temperature":["Temperature"],
        "Humidity":["Humidity"],
        "TemperatureHumidity":["Temperature","Humidity"],
        "Current":["Current"]
    }
    SENSOR_TYPE_CHOICES = [
    (SensorType.Vibration.value, 'Vibration'),
    (SensorType.Temperature.value, 'Temperature'),
    (SensorType.Humidity.value, 'Humidity'),
    (SensorType.TemperatureHumidity.value, 'TemperatureHumidity'),
    (SensorType.Current.value, 'Current'),]

    location = models.CharField(max_length=255)
    subLocation = models.CharField(max_length=255)
    part = models.CharField(max_length=255)
    kind = models.IntegerField(choices=SENSOR_TYPE_CHOICES)
    index = models.IntegerField()
    isOnline = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True,blank=True)

    class interface:
        def __init__(self,data:list) -> None:
            self.data = [data[0],data[1],data[2],Sensor.SensorType[data[3]].value,int(data[4])]
        def __getitem__(self, index):
            return self.data[index]
   
    def getKind(self):
        return Sensor.SensorType(self.kind).name
    
    def getValueKind(self):
        return Sensor.SENSOR_TYPE_VALUES[self.getKind()]

    def getName(self):
        return f"{self.location}/{self.subLocation}/{self.part}/{self.getKind()}/{str(self.index)}"
    def getFilename(self):
        return f"{self.location}_{self.subLocation}_{self.part}_{self.getKind()}_{str(self.index)}"

    def setTime(self):
        self.timestamp = timezone.now()
        return self.timestamp

def selectSensor(data:list):
    try:
        sensor_interface = Sensor.interface(data)
        sensor = Sensor.objects.get(
            location=sensor_interface[0],
            subLocation=sensor_interface[1],
            part=sensor_interface[2],
            kind=sensor_interface[3],
            index=sensor_interface[4]
        )
        return sensor
    except Sensor.DoesNotExist:
        print("error 1 : 존재하지 않는 센서")
        print(f"topic:{data}")
        return False
    except :
        print("error 0 : 예상치 못한 에러")
        print(f"topic:{data}")
        return False

class SensorValue(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE,db_index=True)
    kind = models.CharField(max_length=255)
    value = models.IntegerField()
    
    timestamp= models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['sensor_id',"timestamp","kind"]),
        ]
        constraints = [
            UniqueConstraint(fields=['sensor', 'timestamp', 'kind'], name='unique_sensor_timestamp'),
        ]
    
    @staticmethod
    def create_sensorValue(sensor:Sensor,data:list):
        sensor.setTime()
        sensor.save()
        kinds = data[0]["value"].keys()
        sensor_data_list = [SensorValue(sensor=sensor, timestamp=datetime.strptime(item['time'], '%Y_%m_%d-%H_%M_%S.%f'),value=item['value'][kind],kind=kind) for kind in kinds for item in data ]
        SensorValue.objects.bulk_create(sensor_data_list,  ignore_conflicts=True)

        # for i, kind in enumerate(sensor.getValueType()):
        #     sensorValue = SensorValue(sensor=sensor,kind=kind,value=float(value_list[i]),time= now_time) 
        #     sensorValue.save()
        #     sensorValue.create_sensorValueFile()
    
# class SensorValueFile(models.Model):
#     sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
#     valueKind = models.CharField(max_length=255)
#     time= models.DateTimeField()
#     file = models.FileField(upload_to="data/",max_length=200)
#     def setfile(self,file_content):
#             self.file.save(self.getFileName(),ContentFile(file_content))
#     def getFileName(self):
#         filename_sensor =  f'{self.sensor.location}_{self.sensor.subLocation}_{self.sensor.part}_{self.sensor.getKind()}_{self.sensor.index}'
#         filename_day = f'/{self.time.year:04}_{self.time.month:02}_{self.time.day:02}'
#         filename_time = f'{self.time.hour:02}_{self.time.minute:02}_{self.time.second:02}'
#         filename= f"{filename_sensor}/{filename_day}_raw_{self.valueKind}/{filename_day}-{filename_time}_timeraw_{self.valueKind.lower()}.csv"
#         return filename

# def create_sensorValueFile(self):
#     sensor= sen
#     sensorValue_list= self.sensor.sensorvalue_set.filter(kind=self.kind).fit
#     sensorValue_count = len(sensorValue_list)

#     # print(f"{self.kind}:{sensorValue_count}")
#     if sensorValue_count == 0: return
#     # if sensorValue_count < Sensor.MAX_VALUE_NUM and (self.sensor.time.day == self.time.day): return

#     sensorValue_time_value_list =  sensorValue_list.order_by("time").values_list("time","value")
#     csv_data = StringIO()
#     csv_data.write(u'\ufeff')
#     writer = csv.writer(csv_data)
#     writer.writerow(["",'Time_[s]', "Acceleration[g]"])
    
#     for i, value in enumerate(sensorValue_time_value_list):
#         time = (value[0] - sensorValue_time_value_list[0][0]).seconds
#         writer.writerow([i,time,value[1]])

#     file_content = csv_data.getvalue().encode("utf-8")
#     sensorValueFile= SensorValueFile(sensor=self.sensor,valueKind=self.kind,time= sensorValue_time_value_list[0][0])
#     sensorValueFile.setfile(file_content)
#     sensorValueFile.save()

#     for sensorValue in sensorValue_list:
#         sensorValue.delete()

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
class Plug_type(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100,null=True, blank=True)
    admin_email = models.EmailField(max_length=100,default="DT.TUKOREA@gmail.com",null=True, blank=True) 
    admin_passwd = models.CharField(max_length=100,default="DiK_WiMiS_30!", null=True, blank=True)

    def login_admin(self,ip_address):
        try:
            if self.model == "p100":
                p100 = PyP100.P100(str(ip_address), self.email, self.password)
                p100.handshake()  
                p100.login() 
                return p100
            else: return False
        except:
            return False 
    def get_status(self,ip_address):
        if self.login_admin(ip_address): return True
        else: False
    def turn_off_plug(self,ip_address):
        try:
            plug = self.login_admin(ip_address)
            if not plug : return False
        
            if self.model == "p100":
                plug.turnOff()
                return True
            else: return False
        except:
            return False

    def turn_on_plug(self,ip_address):
        try:
            plug = self.login_admin(ip_address)
            if not plug : return False
        
            if self.model == "p100":
                plug.turnOn()
                return True
            else: return False
        except:
            return False
        
    def get_plug_status(self,ip_address):
        try:
            plug = self.login_admin(ip_address)
            if not plug : return False
            if self.model == "p100":
                plug_status = plug.getDeviceInfo()["device_on"]
                return plug_status
            else: return False
        except:
            return False

class Plug(models.Model):
    location = models.ForeignKey(Location, null=True, blank=True)
    plug_name = models.CharField(max_length=100)
    plug_type = plug = models.ForeignKey(Plug_type,on_delete=models.SET_NULL, null=True, blank=True)

    attention = models.BooleanField(default=False)
    
    
    status = models.BooleanField(default=False)
    target_state = models.BooleanField(default=False)

    plug_status = models.BooleanField(default=False)
    target_plug_state = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.plug_name
        
    def turn_on_plug(self):
        try:
            result = self.plug_type.turn_on_plug(self.ip_address)
            if result:
                self.plug_status = True
                self.save()
            return result
        except:
            return False
        
    def turn_off_plug(self):
        try:
            result = self.plug_type.turn_off_plug(self.ip_address)
            if result:
                self.plug_status = True
                self.save()
            return result
        except:
            return False
    
    def set_plug_status(self):
        try:
            plug_status = self.plug_type.get_plug_status(self.ip_address)
            if self.plug_state != plug_status: 
                self.plug_status = plug_status
                self.save()

            if self.plug_status != self.target_plug_state:
                if self.target_plug_state:
                    self.turn_on_plug()
                else:
                    self.turn_off_plug()
            return True
        except:
            self.plug_status= False
            self.save()
            return False
    
    
    def set_status(self):
        try:
            status = self.plug_type.get_status(self.ip_address)
            if self.state != status: 
                self.status = status
                self.save()
                
            if self.plug_status != self.target_state:
                if self.target_state:
                    self.turn_on_plug()
                else:
                    self.turn_off_plug()
            return True
        except:
            self.status= False
            self.save()
            return False

class Device_type(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    wifi = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

class Device(models.Model):
    location = models.ForeignKey(Location)
    
    plug = models.ForeignKey(Plug,on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')

    device_name = models.CharField(max_length=100)
    device_type= models.ForeignKey(Device_type,on_delete=models.SET_NULL, null=True, blank=True)

    status = models.BooleanField(default=False)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.device_name


class Sensor(models.Model):
    AttachedDevice = models.ForeignKey(Device,on_delete=models.SET_NULL, null=True, blank=True)
    CollectingDevice= models.ForeignKey(Device,on_delete=models.SET_NULL, null=True, blank=True)

    sensor_name = models.CharField(max_length=100)
    kind = models.IntegerField(choices=SENSOR_TYPE_CHOICES)
    model = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=False)
    time = models.DateTimeField(null=True,blank=True)

    class interface:
        def __init__(self,data:list) -> None:
            self.data = [data[0],data[1],data[2],Sensor.SensorType[data[3]].value,int(data[4])]
        def __getitem__(self, index):
            return self.data[index]
   
    def getKind(self):
        return Sensor.SensorType(self.kind).name
    
    def getValueType(self):
        return Sensor.SENSOR_TYPE_VALUES[self.getKind()]

    def getName(self):
        return f"{self.location}/{self.subLocation}/{self.part}/{self.getKind()}/{str(self.index)}"

    def setTime(self):
        self.time = timezone.now()
        return self.time

def selectSensor(data:list):
    try:
        sensor_interface = Sensor.interface(data)
        sensor = Sensor.objects.get(
            location=sensor_interface[0],
            subLocation=sensor_interface[1],
            part=sensor_interface[2],
            kind=sensor_interface[3],
            index=sensor_interface[4]
        )
        return sensor
    except Sensor.DoesNotExist:
        print("error 1 : 존재하지 않는 센서")
        print(f"topic:{data}")
        return False
    except :
        print("error 0 : 예상치 못한 에러")
        print(f"topic:{data}")
        return False