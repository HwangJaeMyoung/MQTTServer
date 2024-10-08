# Generated by Django 5.0.1 on 2024-06-05 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mqtt', '0007_sensorvalue_kind_sensorvalue_value'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='sensorvalue',
            name='unique_sensor_timestamp',
        ),
        migrations.AddConstraint(
            model_name='sensorvalue',
            constraint=models.UniqueConstraint(fields=('sensor', 'timestamp', 'kind'), name='unique_sensor_timestamp'),
        ),
    ]