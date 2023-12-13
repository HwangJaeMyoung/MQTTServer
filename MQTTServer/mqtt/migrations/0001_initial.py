# Generated by Django 2.2.5 on 2023-11-30 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=255)),
                ('subLocation', models.CharField(max_length=255)),
                ('part', models.CharField(max_length=255)),
                ('sensorType', models.IntegerField(choices=[(0, 'Vibration'), (1, 'Temperature'), (2, 'Humidity'), (3, 'TemperatureHumidity'), (4, 'Current')])),
                ('sensorIndex', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SensorValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valueType', models.CharField(max_length=255)),
                ('value', models.FloatField(default=0)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('sensor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mqtt.Sensor')),
            ],
        ),
    ]