from rest_framework import serializers
from .models import Sensor_value

class SensorValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor_value
        fields = '__all__'
