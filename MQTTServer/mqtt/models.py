from django.db import models
from MQTTServer.utils import SENSOR_TYPE_DICT

class Sensor(models.Model):
    SENSOR_TYPE_CHOICES = tuple(SENSOR_TYPE_DICT.items())
    location = models.CharField(max_length=255)
    subLocation = models.CharField(max_length=255)
    part = models.CharField(max_length=255)
    sensorType = models.IntegerField(choices=SENSOR_TYPE_CHOICES)
    sensorIndex = models.IntegerField()
    isOnline = models.BooleanField(default=False)

class SensorValue(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
    valueType = models.CharField(max_length=255)
    value = models.FloatField(default=0)
    time= models.DateTimeField(auto_now_add=True)

