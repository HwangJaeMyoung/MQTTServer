from django.db import models
from enum import Enum

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

class Sensor(models.Model):
    MAX_VALUE_NUM = 4096
    SENSOR_TYPE_CHOICES = [
    (SensorType.Vibration.value, 'Vibration'),
    (SensorType.Temperature.value, 'Temperature'),
    (SensorType.Humidity.value, 'Humidity'),
    (SensorType.TemperatureHumidity.value, 'TemperatureHumidity'),
    (SensorType.Current.value, 'Current'),]

    location = models.CharField(max_length=255)
    subLocation = models.CharField(max_length=255)
    part = models.CharField(max_length=255)
    sensorType = models.IntegerField(choices=SENSOR_TYPE_CHOICES)
    sensorIndex = models.IntegerField()
    isOnline = models.BooleanField(default=False)
    time = models.DateTimeField(null=True,blank=True)

    class interface:
        def __init__(self,data:list) -> None:
            self.data = [data[0],data[1],data[2],SensorType[data[3]],int(data[4])]

        def __getitem__(self, index):
            return self.data[index]

        def __str__(self):
            return f"{self.data[0]}:{self.data[1]}:{self.data[2]}:{self.data[3]}:{self.data[4]}"

    @staticmethod
    def select(data:list):
        try:
            sensor_interface = Sensor.interface(data)
            sensor = Sensor.objects.get(sensor_interface[:])
            return sensor
        except Sensor.DoesNotExist:
            print("error 1 : 존재하지 않는 센서")
            print(f"topic:{data}")
            return False
        except :
            print("error 0 : 예상치 못한 에러")
            print(f"topic:{data}")
            return False
        
    def getType(self):
        return SensorType(self.sensorType).name
    
    def getValueType(self):
        return SENSOR_TYPE_VALUES[self.getType()]

    def getData(self):
        return [self.location,self.subLocation,self.part,SensorType(self.sensorType),str(self.sensorIndex)]
    
    def 


class SensorValue(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
    valueType = models.CharField(max_length=255)
    value = models.FloatField(default=0)
    time= models.DateTimeField()


class SensorValueFile(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
    valueType = models.CharField(max_length=255)
    time= models.DateTimeField()
    file = models.FileField(upload_to="data/",max_length=200)

