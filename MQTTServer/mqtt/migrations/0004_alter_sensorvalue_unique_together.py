# Generated by Django 5.0.1 on 2024-06-04 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mqtt', '0003_sensorvalue_mqtt_sensor_sensor__01c873_idx'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sensorvalue',
            unique_together={('sensor', 'timestamp')},
        ),
    ]
