from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone

from enum import Enum
import csv
from io import StringIO 

class Sensor(models.Model):
    MAX_VALUE_NUM = 4096
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

    @staticmethod
    def select(data:list):
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
        
    def getKind(self):
        return Sensor.SensorType(self.kind).name
    
    def getValueType(self):
        return Sensor.SENSOR_TYPE_VALUES[self.getKind()]

    def getName(self):
        return f"{self.location}/{self.subLocation}/{self.part}/{self.getKind()}/{str(self.index)}"

    
    def setTime(self):
        self.time = timezone.now()
        return self.time


class SensorValue(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
    kind = models.CharField(max_length=255)
    value = models.FloatField(default=0)
    time= models.DateTimeField()
    
    @staticmethod
    def create_sensorValue(sensor:Sensor,value_list:list):
        now_time = sensor.setTime()
        sensor.save()
        for i, kind in enumerate(sensor.getValueType()):
            sensorValue = SensorValue(sensor=sensor,kind=kind,value=float(value_list[i]),time= now_time) 
            sensorValue.save()
            sensorValue.create_sensorValueFile()


    def create_sensorValueFile(self):
        sensorValue_list= self.sensor.sensorvalue_set.filter(kind=self.kind)
        sensorValue_count = len(sensorValue_list)
        print(f"{self.kind}:{sensorValue_count}")
        if sensorValue_count == 0: return
        if sensorValue_count < Sensor.MAX_VALUE_NUM and (self.sensor.time.day == self.time.day): return

        sensorValue_time_value_list =  sensorValue_list.order_by("time").values_list("time","value")
        csv_data = StringIO()
        csv_data.write(u'\ufeff')
        writer = csv.writer(csv_data)
        writer.writerow(["",'Time_[s]', "Acceleration[g]"])
        
        for i, value in enumerate(sensorValue_time_value_list):
            time = (value[0] - sensorValue_time_value_list[0][0]).seconds
            writer.writerow([i,time,value[1]])

        file_content = csv_data.getvalue().encode("utf-8")
        sensorValueFile= SensorValueFile(sensor=self.sensor,valueKind=self.kind,time= sensorValue_time_value_list[0][0])
        sensorValueFile.setfile(file_content)
        sensorValueFile.save()

        for sensorValue in sensorValue_list:
            sensorValue.delete()
    

class SensorValueFile(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
    valueKind = models.CharField(max_length=255)
    time= models.DateTimeField()
    file = models.FileField(upload_to="data/",max_length=200)
    def setfile(self,file_content):
            self.file.save(self.getFileName(),ContentFile(file_content))
    def getFileName(self):
        filename_sensor =  f'{self.sensor.location}_{self.sensor.subLocation}_{self.sensor.part}_{self.sensor.getKind()}_{self.sensor.index}'
        filename_day = f'/{self.time.year:04}_{self.time.month:02}_{self.time.day:02}'
        filename_time = f'{self.time.hour:02}_{self.time.minute:02}_{self.time.second:02}'
        filename= f"{filename_sensor}/{filename_day}_raw_{self.valueKind}/{filename_day}-{filename_time}_timeraw_{self.valueKind.lower()}.csv"
        return filename


