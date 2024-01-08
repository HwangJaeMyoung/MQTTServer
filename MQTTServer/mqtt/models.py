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
    time = models.DateTimeField(null=True,blank=True)

class SensorValue(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
    valueType = models.CharField(max_length=255)
    value = models.FloatField(default=0)
    time= models.DateTimeField(auto_now_add=True)

class SensorValueFile(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE)
    valueType = models.CharField(max_length=255)
    time= models.DateTimeField()
    file = models.FileField(upload_to="data/",max_length=200)




