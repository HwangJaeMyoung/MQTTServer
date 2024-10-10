from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime
from enum import Enum
import csv
from io import StringIO 
from PyP100 import PyP100
from django.db.models import UniqueConstraint
import logging

logger = logging.getLogger("monitor")

# class Sensor(models.Model):
#     MAX_VALUE_NUM = 4096
#     class SensorType(Enum):
#         Vibration = 0
#         Temperature = 1
#         Humidity = 2
#         TemperatureHumidity = 3
#         Current = 4
#     SENSOR_TYPE_VALUES = {
#         "Vibration" :["x","y","z"],
#         "Temperature":["Temperature"],
#         "Humidity":["Humidity"],
#         "TemperatureHumidity":["Temperature","Humidity"],
#         "Current":["Current"]
#     }
#     SENSOR_TYPE_CHOICES = [
#     (SensorType.Vibration.value, 'Vibration'),
#     (SensorType.Temperature.value, 'Temperature'),
#     (SensorType.Humidity.value, 'Humidity'),
#     (SensorType.TemperatureHumidity.value, 'TemperatureHumidity'),
#     (SensorType.Current.value, 'Current'),]

#     location = models.CharField(max_length=255)
#     subLocation = models.CharField(max_length=255)
#     part = models.CharField(max_length=255)
#     kind = models.IntegerField(choices=SENSOR_TYPE_CHOICES)
#     index = models.IntegerField()
#     isOnline = models.BooleanField(default=False)
#     timestamp = models.DateTimeField(null=True,blank=True)

#     class interface:
#         def __init__(self,data:list) -> None:
#             self.data = [data[0],data[1],data[2],Sensor.SensorType[data[3]].value,int(data[4])]
#         def __getitem__(self, index):
#             return self.data[index]
   
#     def getKind(self):
#         return Sensor.SensorType(self.kind).name
    
#     def getValueKind(self):
#         return Sensor.SENSOR_TYPE_VALUES[self.getKind()]

#     def getName(self):
#         return f"{self.location}/{self.subLocation}/{self.part}/{self.getKind()}/{str(self.index)}"
#     def getFilename(self):
#         return f"{self.location}_{self.subLocation}_{self.part}_{self.getKind()}_{str(self.index)}"

#     def setTime(self):
#         self.timestamp = timezone.now()
#         return self.timestamp

# class SensorValue(models.Model):
#     sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE,db_index=True)
#     kind = models.CharField(max_length=255)
#     value = models.IntegerField()
    
#     timestamp= models.DateTimeField()

#     class Meta:
#         indexes = [
#             models.Index(fields=['sensor_id',"timestamp","kind"]),
#         ]
#         constraints = [
#             UniqueConstraint(fields=['sensor', 'timestamp', 'kind'], name='unique_sensor_timestamp'),
#         ]
    
#     @staticmethod
#     def create_sensorValue(sensor:Sensor,data:list):
#         sensor.setTime()
#         sensor.save()
#         kinds = data[0]["value"].keys()
#         sensor_data_list = [SensorValue(sensor=sensor, timestamp=datetime.strptime(item['time'], '%Y_%m_%d-%H_%M_%S.%f'),value=item['value'][kind],kind=kind) for kind in kinds for item in data ]
#         SensorValue.objects.bulk_create(sensor_data_list,  ignore_conflicts=True)

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
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    def select(self,name:str):
        try:
            location = self.child.get(name=name)
            return location
        except Location.DoesNotExist:
            try:
                device =self.device_set.get(name=name)
                return device
            except Device.DoesNotExist:
                logger.warning(f"excute select() not exist location or device matched name: {name}")
                return False
        
class Plug_type(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100,null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    wifi = models.BooleanField(default=False)
    admin_email = models.EmailField(max_length=100,default="DT.TUKOREA@gmail.com",null=True, blank=True) 
    admin_passwd = models.CharField(max_length=100,default="DiK_WiMiS_30!", null=True, blank=True)

    def login_admin(self,ip_address):
        logger.debug(f"excute login_admin()")
        try:
            if self.model.lower() == "p100":
                logger.debug(f"excute login_admin() case p100")
                p100 = PyP100.P100(str(ip_address), self.admin_email, self.admin_passwd)
                p100.handshake()  
                p100.login()
                return p100
            else: return False
        except:
            logger.warning(f"excute login_admin() error handshake")
            return False 
    def get_status(self,ip_address):
        if self.login_admin(ip_address):return True
        else: return False
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
    location = models.ForeignKey(Location,on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)

    plug_type=  models.OneToOneField(Plug_type,on_delete=models.SET_NULL, null=True, blank=True)

    attention = models.BooleanField(default=False)
    
    status = models.BooleanField(default=False)
    target_status = models.BooleanField(default=False)

    plug_status = models.BooleanField(default=False)
    target_plug_status = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def set_status(self):
        if self.plug_type.wifi == False: return False
        status = self.plug_type.get_status(self.ip_address)
        if self.status != status: 
            self.status = status
            self.save()
        if self.target_status == True and self.status == False:return False
        return True
    
    def set_plug_status(self):
        if self.plug_type.wifi == False: return False
        plug_status = self.plug_type.get_plug_status(self.ip_address)
        if self.plug_status != plug_status: 
            self.plug_status = plug_status
            self.save()
        if self.plug_status == self.target_plug_status: return True

        if self.target_plug_status:
            result = self.plug_type.turn_on_plug(self.ip_address)
        else:
            result = self.plug_type.turn_off_plug(self.ip_address)
            
        if result == False:return False
        self.plug_status = self.target_plug_status
        self.save()
        return True
    
class Device_type(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100,null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    wifi = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_status(self,ip_address):
        if self.model == "esp32":
            pass
        return True

class Device(models.Model):
    location = models.ForeignKey(Location,on_delete=models.SET_NULL, null=True, blank=True)
    
    plug = models.ForeignKey(Plug,on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')

    name = models.CharField(max_length=100)
    device_type= models.OneToOneField(Device_type,on_delete=models.SET_NULL, null=True, blank=True)

    target_state = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def set_status(self):
        if self.device_type.wifi == False: return False
        status = self.device_type.get_status(self.ip_address)
        if self.state != status: 
            self.status = status
            self.save()
        if self.target_state == True and self.status == False:return False
        return True

    def select(self,name:str):
        try:
            device =self.child.get(name=name)
            return device
        except Device.DoesNotExist:
            try:
                sensor =self.attached_sensors.get(name=name)
                return sensor
            except Sensor.DoesNotExist:
                logger.warning(f"excute select() not exist  device or sensor matched name: {name}")
                return False

class Sensor_type(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=50, blank=True, null=True)    
    properties = models.JSONField(default=list, blank=True, null=True)  
    def save(self, *args, **kwargs):
        if not self.properties:
            if self.name == "Vibration":
                self.properties = ["x", "y", "z"]
            elif self.name == "Temperature":
                self.properties = ["Temperature"]
            elif self.name == "Humidity":
                self.properties = ["Humidity"]
            elif self.name == "Current":
                self.properties = ["Current"]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    AttachedDevice = models.ForeignKey(Device,on_delete=models.SET_NULL, null=True, blank=True,related_name='attached_sensors')
    CollectingDevice= models.ForeignKey(Device,on_delete=models.SET_NULL, null=True, blank=True,related_name='collecting_sensors')
    name = models.CharField(max_length=100)
    sensor_type = models.OneToOneField(Sensor_type,on_delete=models.SET_NULL,null=True, blank=True)
    status = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
class Sensor_networking(models.Model):
    sensor=models.ForeignKey(Sensor,on_delete=models.CASCAD, null=True, blank=True,)
    topic = models.CharField(max_length=100)
    action_type = models.CharField(max_length=15, choices=[("Register", "Register"), ("Confirm", "Confirm"), ("Value", "Value"),("Other", "Other")])
    direction = models.BooleanField(default=True)  # True: Received, False: Sent
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True,blank=True)

class Sensor_value(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE,db_index=True)
    value_type = models.CharField(max_length=255)
    value = models.FloatField()
    timestamp= models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['sensor_id',"timestamp","value_type"]),
        ]
        constraints = [
            UniqueConstraint(fields=['sensor', 'timestamp', 'value_type'], name='unique_sensor_timestamp'),
        ]

def select(name:str):
    try:
        location = Location.objects.get(name=name)
        return location
    except Location.DoesNotExist:
        try:
            device = Device.objects.get(name=name)
            return device
        except Device.DoesNotExist:
            logger.warning(f"excute select() not exist location or device matched name: {name}")
            return False
    
def select_sensor(data:list):
    selected_object = select(data[0])
    for name in data[1:]:
        selected_object = selected_object.select(name)
        if not selected_object: return False
    if isinstance(selected_object, Sensor):return selected_object
    else:
        logger.warning(f"excute selectSensor() not sensor: {selected_object}")
        return False 

def create_sensorValue(sensor:Sensor,data:list):
    for item in data:
        key = item["value"].keys()
        if list(key) !=sensor.sensor_type.properties:
            logging.warning(f"excute create_sensorValue porperty not match {key}:{sensor.sensor_type.properties}")
            return False
        
    properties = sensor.sensor_type.properties
    sensor_data_list = [Sensor_value( sensor=sensor,
                                     timestamp=datetime.strptime(item['time'], '%Y_%m_%d-%H_%M_%S.%f'),
                                     value=item['value'][property],value_type = property) for property in properties  for item in data ]    
    Sensor_value.objects.bulk_create(sensor_data_list,  ignore_conflicts=True)
    return True

def select_network(topic:str):
    try:
        network = Sensor_networking.objects.get(topic = topic)
        return network
    except Sensor_networking.DoesNotExist:
        logger.warning(f"excute select_sensor_from_network() not exist sensor_network matched topic:{topic}")
        return False