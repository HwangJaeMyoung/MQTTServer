# Generated by Django 5.0.1 on 2024-06-04 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mqtt', '0005_alter_sensorvalue_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensorvalue',
            name='value',
        ),
    ]