from django.db import models

SENSOR_TYPE_LIST = {
    0:"Vibration",
    1:"Temperature",
    2:"Humidity",
    3:"TemperatureHumidity",
    4:"Current"
    }

class Sensor(models.Model):
    SENSOR_TYPE_CHOICES = tuple(SENSOR_TYPE_LIST.items())
    location = models.CharField(max_length=255)
    subLocation = models.CharField(max_length=255)
    part = models.CharField(max_length=255)
    sensorType = models.IntegerField(choices=SENSOR_TYPE_CHOICES)
    sensorIndex = models.IntegerField()

class SensorValue(models.Model):
    sensor_id =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
    valueType = models.CharField(max_length=255)
    value = models.FloatField(default=0)
    time= models.DateTimeField(auto_now_add=True)


