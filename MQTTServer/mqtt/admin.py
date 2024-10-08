from django.contrib import admin
from .models import Sensor , SensorValue #,SensorValueFile
from django import forms
# import csv
from django.http import HttpResponse
# import matplotlib
# matplotlib.use('Agg')  

# import matplotlib.dates as mdates
# import io
# from django.utils.safestring import mark_safe
# import numpy as np
from io import BytesIO, StringIO

from .models import Sensor
import zipfile

from django.shortcuts import render
from django.contrib import messages
from django.db import connection
from django.db.models import Min, Max
import pandas as pd
from datetime import timedelta,datetime

import matplotlib.pyplot as plt
import base64


class DateRangeForm(forms.Form):
    start_date = forms.DateTimeField(label='Start Date', widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(label='End Date', widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))

    def __init__(self, *args, **kwargs):
        super(DateRangeForm, self).__init__(*args, **kwargs)
        

        min_max_values = SensorValue.objects.aggregate(
            min_timestamp=Min('timestamp'),
            max_timestamp=Max('timestamp')
        )

        self.fields['start_date'].initial = min_max_values['min_timestamp']
        self.fields['end_date'].initial = min_max_values['max_timestamp']

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("get_name","timestamp","is_online")
    list_filter = ('location', 'subLocation','kind',)
    readonly_fields = ("index",)
    actions = ["manage_sensor_data"]

    def get_name(self, obj:Sensor):
        return obj.getName()
    
    def is_online(self,obj):
        msg = "Offline"
        if obj.isOnline:
            msg = "Online"
        return msg
    
    def save_model(self, request, obj:Sensor, form, change):
        if not change:
            sensor_set = Sensor.objects.filter(
                location = obj.location,
                subLocation = obj.subLocation,
                part = obj.part,
                kind= obj.kind)
            if sensor_set.exists():
                obj.index= len(sensor_set) + 1
            else:
                obj.index= 1
        obj.save()

    def delete_model(self, request, obj:Sensor):
        sensor_set = Sensor.objects.filter(
            location = obj.location,
            subLocation = obj.subLocation,
            part = obj.part,
            kind= obj.kind)
        if len(sensor_set) == 1:
            pass
        else:
            for sensor in sensor_set:
                if obj.index < sensor.index:
                    sensor.index -= 1
                    sensor.save()
        obj.delete()
    
    def manage_sensor_data(self,request,queryset):
        if not request.method == 'POST': return

        if 'delete_selected_data' in request.POST or 'download_selected_data' in request.POST or 'plot_selected_data' in request.POST:
            form = DateRangeForm(request.POST)
            if not form.is_valid(): return
            sensor_ids = queryset.values_list('id', flat=True)
            if not sensor_ids: return
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            if 'delete_selected_data'  in request.POST:
                messages.success(request, f"Sensor data from {start_date} to {end_date} for selected sensors has been deleted.")
                return self.delete_selected_data_by_date_range(start_date,end_date,queryset)
            elif 'download_selected_data' in request.POST:
                messages.success(request, f"Sensor data from {start_date} to {end_date} for selected sensors has been download.")
                return self.download_selected_data_by_date_range(start_date,end_date,queryset)
            elif 'plot_selected_data' in request.POST:
                plot = self.plot_data_by_date_range(start_date,end_date,queryset)
                
                context = {'form': form, 'queryset': queryset, 'plot': plot}
        else:
            form = DateRangeForm()
            context = {
                'form': form,
                'queryset': queryset
            }
        return render(request, 'admin/sensors/download_by_date_range.html', context)
        
    def delete_selected_data_by_date_range(self, start_date,end_date,queryset):
        sensor_ids = queryset.values_list('id', flat=True)
        if not sensor_ids: return
        with connection.cursor() as cursor:
            delete_query = """
                delete FROM mqtt_sensorValue
                WHERE timestamp >= %s AND timestamp <= %s
            """
            delete_query += "and (false"
            for sensor_id in sensor_ids:
                delete_query += " OR sensor_id = %s"
            delete_query += ");"                        
            cursor.execute(delete_query, [start_date, end_date] + list(sensor_ids))
        return 
    
    def download_selected_data_by_date_range(self, start_date,end_date,queryset):
        sensor_ids = queryset.values_list('id', flat=True)
        zip_filename = 'ICCMS.zip'
        zip_buffer = BytesIO()
        if not sensor_ids: return
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            with connection.cursor() as cursor:
                for sensor in queryset:
                    # kind_list = SensorValue.objects.filter(sensor_id=sensor.id).values_list('kind', flat=True).distinct()
                    kind_list= sensor.getValueKind()
                    current_date = start_date
                    while current_date.date() <= end_date.date():
                        next_date = current_date + timedelta(days=1)
                        for kind in kind_list:
                            sql_query = f"""
                                WITH filtered_sensorvalue AS (
                                    SELECT timestamp, value,kind
                                    FROM mqtt_sensorvalue
                                    WHERE timestamp >= '{current_date.strftime('%Y-%m-%d') if current_date != start_date else start_date.strftime('%Y-%m-%d %H:%M:%S') }'
                                    AND timestamp <= '{next_date.strftime('%Y-%m-%d') if next_date.date() <= end_date.date() else next_date.strftime('%Y-%m-%d %H:%M:%S')}'
                                    AND sensor_id = %s 
                                    AND kind  = %s
                                    order by timestamp
                                ) ,
                                min_timestamp AS (
                                    SELECT MIN(timestamp) AS min_timestamp
                                    FROM filtered_sensorvalue
                                )
                                SELECT EXTRACT(EPOCH FROM (timestamp -  min_timestamp)) AS "Time_[s]", value AS "Acceleration[g]"
                                FROM filtered_sensorvalue, min_timestamp;
                            """
                            cursor.execute(sql_query,[sensor.id,kind])
                            columns = [col[0] for col in cursor.description]
                            data = cursor.fetchall()
                            df_day = pd.DataFrame(data, columns=columns)
                            csv_buffer = StringIO()
                            df_day.to_csv(csv_buffer, index=False)
                            file_name = f"{sensor.getFilename()}/{current_date.strftime('%Y-%m-%d')}_{kind}.csv"
                            print(f"ready {file_name}")
                            zip_file.writestr(file_name,csv_buffer.getvalue())
                        current_date = next_date
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        return response

    manage_sensor_data.short_description = 'Management data by date range for selected sensors'
    get_name.short_description = 'Name'

    def plot_data_by_date_range(self, start_date,end_date,queryset):
        with connection.cursor() as cursor:
            dfs = []
            kinds= []
            for i,sensor in enumerate(queryset):
                dfs.append([])
                total_rows_query = f"""
                    SELECT COUNT(*)
                    FROM mqtt_sensorvalue
                    WHERE timestamp >= '{start_date}' 
                    AND timestamp <= '{end_date}'
                    AND sensor_id = %s
                    AND Kind  = %s
                """

                for kind in sensor.getValueKind():
                    cursor.execute(total_rows_query, (sensor.id,kind))
                    total_rows = cursor.fetchone()[0]
                    interval = max(1, int(total_rows//1000))
                    sql_query = f"""
                                SELECT value, timestamp
                                FROM (
                                    SELECT value, timestamp, ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY timestamp) AS row_num
                                    FROM mqtt_sensorvalue
                                    WHERE timestamp >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}' 
                                    AND timestamp <= '{end_date.strftime('%Y-%m-%d %H:%M:%S')}'
                                    AND sensor_id = %s 
                                    AND Kind  = %s
                                ) subquery
                                WHERE row_num %% {interval} = 0"""
                    a= datetime.now()
                    cursor.execute(sql_query,(sensor.id,kind))
                    columns = [col[0] for col in cursor.description]
                    data = cursor.fetchall()
                    dfs[i].append(pd.DataFrame(data, columns=columns))
                    b= datetime.now()
                    print(b-a)

                kinds.append(sensor.getValueKind())
                
            max_kind= max([len(sensor.getValueKind()) for sensor in queryset])
            fig, axs= plt.subplots(nrows=max(2,len(queryset)), ncols=max_kind)
            fig.set_size_inches(20, 10)
            for i, kind in enumerate(kinds):
                for j in range(len(kind)):
                    kind_df = dfs[i][j]
                    axs[i,j].plot(kind_df['timestamp'], kind_df['value'], label=f'{kind[j]}')
                    axs[i,j].set_xlabel('Time')
                    axs[i,j].set_ylabel('Value')
                    axs[i,j].legend()
                    axs[i,j].set_xlim([start_date, end_date])
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight', pad_inches=0.1)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plot = base64.b64encode(image_png).decode('utf-8')
        return plot

@admin.register(SensorValue)
class SensorValueAdmin(admin.ModelAdmin):
    list_display = ('sensor_id', 'timestamp')
    actions = ['delete_selected_data']