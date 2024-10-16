# Generated by Django 4.1 on 2024-10-14 01:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("attention", models.BooleanField(default=False)),
                ("target_state", models.BooleanField(default=False)),
                ("status", models.BooleanField(default=False)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "device",
            },
        ),
        migrations.CreateModel(
            name="Device_type",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("model", models.CharField(blank=True, max_length=100, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("wifi", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "device_type",
            },
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="child",
                        to="mqtt.location",
                    ),
                ),
            ],
            options={
                "db_table": "location",
            },
        ),
        migrations.CreateModel(
            name="Plug_type",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("model", models.CharField(blank=True, max_length=100, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("wifi", models.BooleanField(default=False)),
                (
                    "admin_email",
                    models.EmailField(
                        blank=True,
                        default="DT.TUKOREA@gmail.com",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "admin_passwd",
                    models.CharField(
                        blank=True, default="DiK_WiMiS_30!", max_length=100, null=True
                    ),
                ),
            ],
            options={
                "db_table": "plug_type",
            },
        ),
        migrations.CreateModel(
            name="Sensor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("attention", models.BooleanField(default=False)),
                (
                    "attached_device",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="attached_sensors",
                        to="mqtt.device",
                    ),
                ),
                (
                    "collecting_device",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="collecting_sensors",
                        to="mqtt.device",
                    ),
                ),
            ],
            options={
                "db_table": "sensor",
            },
        ),
        migrations.CreateModel(
            name="Sensor_type",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("model", models.CharField(blank=True, max_length=50, null=True)),
                ("properties", models.JSONField(blank=True, default=list, null=True)),
            ],
            options={
                "db_table": "sensor_type",
            },
        ),
        migrations.CreateModel(
            name="Sensor_value_file",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value_type", models.CharField(max_length=255)),
                ("timestamp", models.DateTimeField()),
                ("file", models.FileField(max_length=200, upload_to="data/")),
                (
                    "device",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="mqtt.device",
                    ),
                ),
                (
                    "sensor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="mqtt.sensor",
                    ),
                ),
            ],
            options={
                "db_table": "sensor_value_file",
            },
        ),
        migrations.CreateModel(
            name="Sensor_value",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value_type", models.CharField(max_length=255)),
                ("value", models.FloatField()),
                ("timestamp", models.DateTimeField(blank=True, null=True)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mqtt.device"
                    ),
                ),
                (
                    "sensor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mqtt.sensor"
                    ),
                ),
            ],
            options={
                "db_table": "sensor_value",
            },
        ),
        migrations.CreateModel(
            name="Sensor_networking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("topic", models.CharField(max_length=100)),
                (
                    "action_type",
                    models.CharField(
                        choices=[
                            ("Register", "Register"),
                            ("Confirm", "Confirm"),
                            ("Value", "Value"),
                        ],
                        max_length=15,
                    ),
                ),
                ("direction", models.BooleanField(default=True)),
                ("status", models.BooleanField(default=False)),
                ("network_status", models.BooleanField(default=False)),
                ("timestamp", models.DateTimeField(blank=True, null=True)),
                (
                    "device",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mqtt.device",
                    ),
                ),
                (
                    "sensor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mqtt.sensor",
                    ),
                ),
            ],
            options={
                "db_table": "sensor_networking",
            },
        ),
        migrations.AddField(
            model_name="sensor",
            name="sensor_type",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="mqtt.sensor_type",
            ),
        ),
        migrations.CreateModel(
            name="Plug",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("attention", models.BooleanField(default=False)),
                ("status", models.BooleanField(default=False)),
                ("target_status", models.BooleanField(default=False)),
                ("plug_status", models.BooleanField(default=False)),
                ("target_plug_status", models.BooleanField(default=False)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="mqtt.location",
                    ),
                ),
                (
                    "plug_type",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="mqtt.plug_type",
                    ),
                ),
            ],
            options={
                "db_table": "plug",
            },
        ),
        migrations.AddField(
            model_name="device",
            name="device_type",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="mqtt.device_type",
            ),
        ),
        migrations.AddField(
            model_name="device",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="mqtt.location",
            ),
        ),
        migrations.AddField(
            model_name="device",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="child",
                to="mqtt.device",
            ),
        ),
        migrations.AddField(
            model_name="device",
            name="plug",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="mqtt.plug",
            ),
        ),
        migrations.AddIndex(
            model_name="sensor_value",
            index=models.Index(
                fields=["sensor_id", "timestamp", "value_type"],
                name="sensor_valu_sensor__776b1d_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="sensor_value",
            constraint=models.UniqueConstraint(
                fields=("sensor", "timestamp", "value_type"),
                name="unique_sensor_timestamp",
            ),
        ),
    ]
