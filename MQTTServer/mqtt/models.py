from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime
from enum import Enum
import csv
from io import StringIO 
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
        

    # def create_sensorValueFile(self):
    #     sensorValue_list= self.sensor.sensorvalue_set.filter(kind=self.kind)
    #     sensorValue_count = len(sensorValue_list)
    #     print(f"{self.kind}:{sensorValue_count}")
    #     if sensorValue_count == 0: return
    #     if sensorValue_count < Sensor.MAX_VALUE_NUM and (self.sensor.time.day == self.time.day): return

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

class SmartPlug(models.Model):
    location = models.ForeignKey(Location)
    plug_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)  # 0: OFF, 1: ON
    plug_status = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.plug_name

class Arduino(models.Model):
    location = models.ForeignKey(Location)
    smart_plug = models.ForeignKey(SmartPlug,on_delete=models.SET_NULL, null=True, blank=True)
    arduino_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.arduino_name

 
class Sensor(models.Model):
    class SensorType(Enum):
        Vibration = 0
        Temperature = 1
        Humidity = 2
        TemperatureHumidity = 3
        Current = 4
    SENSOR_TYPE_VALUES = {
        "Vibration" :["X","Y","Z"],
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

# class Sensor(models.Model):
#     arduino = models.ForeignKey(Arduino, on_delete=models.CASCADE)
#     sensor_name = models.CharField(max_length=100)
#     sensor_type = models.CharField(max_length=50)

#     def __str__(self):
#         return self.sensor_name

# class SensorData(models.Model):
#     sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
#     value = models.FloatField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.sensor.sensor_name} - {self.value} at {self.timestamp}"

