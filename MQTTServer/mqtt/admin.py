from django.contrib import admin
from .models import Sensor, SensorValue,SensorValueFile
import csv
from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
from django.utils.safestring import mark_safe
import numpy as np
from io import BytesIO, StringIO
import base64
from MQTTServer.utils import SENSOR_TYPE_DICT, SENSOR_VALUE_MAP_DICT
import zipfile


class SensorAdmin(admin.ModelAdmin):
    list_display = ("get_name","is_online")
    list_filter = ('location', 'subLocation','sensorType',)
    readonly_fields = ("sensorIndex","get_graph",)
    actions = ["download_sensor_data",]
    def get_graph(self, obj):
        if obj.sensorvalue_set.exists():
            plt.figure(figsize=(6, 4))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
            color = ["r","g","b"]
            legend = []
            for i,valueType in enumerate(SENSOR_VALUE_MAP_DICT[SENSOR_TYPE_DICT[obj.sensorType]]):
                try:
                    data= obj.sensorvalue_set.order_by("time").filter(valueType = valueType).values_list('time', 'value')
                    dates,values = zip(*data)
                    plt.plot_date(dates, values,f"-{color[i]}")
                    plt.title('Sensor Data Graph')
                    plt.xlabel('Date')
                    plt.ylabel('Value')
                    plt.xticks([])
                    legend.append(SENSOR_VALUE_MAP_DICT[SENSOR_TYPE_DICT[obj.sensorType]][i])
                except:
                    pass
            plt.legend(legend)
            plt.gcf().autofmt_xdate()
            # 그래프 이미지를 BytesIO로 변환
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            return mark_safe(f'<img src="data:image/png;base64,{image_base64}" />')
        else:
            return None

    def get_name(self, obj):
        return f"{obj.location}/{obj.subLocation}/{obj.part}/{SENSOR_TYPE_DICT[obj.sensorType]}/{obj.sensorIndex}"
    
    def is_online(self,obj):
        msg = "Offline"
        if obj.isOnline:
            msg = "Online"
        return msg
    
    def download_sensor_data(self, request, queryset):
        zip_filename = 'ICCMS.zip'
        zip_buffer = BytesIO()            
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for obj in queryset:
                for file in obj.sensorvaluefile_set.all():
                    with file.file.open() as f:
                        zip_file.writestr(file.file.name,f.read())

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        return response
    
    def save_model(self, request, obj, form, change):
        if not change:
            sensor_set = Sensor.objects.filter(
                location = obj.location,
                subLocation = obj.subLocation,
                part = obj.part,
                sensorType= obj.sensorType)
            if sensor_set.exists():
                obj.sensorIndex= len(sensor_set) + 1
            else:
                obj.sensorIndex= 1
        obj.save()

    def delete_model(self, request, obj):
        sensor_set = Sensor.objects.filter(
            location = obj.location,
            subLocation = obj.subLocation,
            part = obj.part,
            sensorType= obj.sensorType)
        if len(sensor_set) == 1:
            pass
        else:
            for sensor in sensor_set:
                if obj.sensorIndex < sensor.index:
                    sensor.index -= 1
                    sensor.save()
        obj.delete()
    
    download_sensor_data.short_description = 'Download csv zip'
    get_graph.short_description = "Graph"
    get_name.short_description = 'Name'

admin.site.register(Sensor,SensorAdmin)
admin.site.register(SensorValue)
admin.site.register(SensorValueFile)