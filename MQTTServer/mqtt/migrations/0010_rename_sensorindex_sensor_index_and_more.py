# Generated by Django 5.0.4 on 2024-05-08 16:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mqtt", "0009_alter_sensorvalue_time"),
    ]

    operations = [
        migrations.RenameField(
            model_name="sensor",
            old_name="sensorIndex",
            new_name="index",
        ),
        migrations.RenameField(
            model_name="sensorvalue",
            old_name="valueType",
            new_name="type",
        ),
        migrations.RemoveField(
            model_name="sensor",
            name="sensorType",
        ),
        migrations.AddField(
            model_name="sensor",
            name="type",
            field=models.IntegerField(
                choices=[
                    (0, "Vibration"),
                    (1, "Temperature"),
                    (2, "Humidity"),
                    (3, "TemperatureHumidity"),
                    (4, "Current"),
                ],
                default=0,
            ),
            preserve_default=False,
        ),
    ]