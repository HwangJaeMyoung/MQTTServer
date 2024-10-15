from .models import Sensor,Sensor_value
from django.shortcuts import render, get_object_or_404, redirect 

from .client import get_maintenance, end_maintenance, start_maintenance

import logging 

logger = logging.getLogger("mqtt")

def sensor_data_list(request):
    data = Sensor.objects.all()
    return render(request, 'sensors/sensor_data_list.html', {'data': data})

def sensor_data_detail(request, pk):
    data = get_object_or_404(Sensor_value, pk=pk)
    return render(request, 'sensors/sensor_data_detail.html', {'data': data})

def sensor_data_new(request):
    # if request.method == "POST":
    #     form = SensorDataForm(request.POST)
    #     if form.is_valid():
    #         data = form.save()
    #         return redirect('sensor_data_detail', pk=data.pk)
    # else:
    #     form = SensorDataForm()
    form = 0
    return render(request, 'sensors/sensor_data_edit.html', {'form': form})

# def sensor_data_edit(request, pk):
#     data = get_object_or_404(SensorData, pk=pk)
#     if request.method == "POST":
#         form = SensorDataForm(request.POST, instance=data)
#         if form.is_valid():
#             data = form.save()
#             return redirect('sensor_data_detail', pk=data.pk)
#     else:
#         form = SensorDataForm(instance=data)
#     return render(request, 'sensors/sensor_data_edit.html', {'form': form})

# def sensor_data_delete(request, pk):
#     data = get_object_or_404(SensorData, pk=pk)
#     data.delete()
#     return redirect('sensor_data_list')
