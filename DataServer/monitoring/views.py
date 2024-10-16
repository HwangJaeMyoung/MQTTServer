from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import Plug,Sensor,Location,Device,Sensor_value
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt


# # Create your views here.
# def sensor_data_view(request, sensor_id):
#     sensor = get_object_or_404(Sensor, pk=sensor_id)
#     sensor_values = Sensor_value.objects.filter(sensor=sensor).order_by('-timestamp')
#     data = {
#         'sensor_name': sensor.name,
#         'sensor_type': sensor.sensor_type.name,
#         'sensor_values': [
#             {
#                 'value_type': value.value_type,
#                 'value': value.value,
#                 'timestamp': value.timestamp
#             } for value in sensor_values
#         ]
#     }
#     return JsonResponse(data)

# # Device의 상태를 얻기 위한 view
# def device_status_view(request, device_id):
#     device = get_object_or_404(Device, pk=device_id)
#     data = {
#         'device_name': device.name,
#         'device_status': device.status,
#         'target_status': device.target_status,
#         'attention': device.attention
#     }
#     return JsonResponse(data)

# # Plug 상태를 얻기 위한 view
# def plug_status_view(request, plug_id):
#     plug = get_object_or_404(Plug, pk=plug_id)
#     data = {
#         'plug_name': plug.name,
#         'plug_status': plug.plug_status,
#         'target_plug_status': plug.target_plug_status,
#         'attention': plug.attention,
#     }
#     return JsonResponse(data)

@csrf_exempt
def turn_on_plug_status_view(request, plug_id):
    plug = get_object_or_404(Plug,pk=plug_id)
    plug.target_status = True
    plug.save()
    return HttpResponse("success")

@csrf_exempt
def turn_off_plug_status_view(request, plug_id):
    plug = get_object_or_404(Plug,pk=plug_id)
    plug.target_status = False
    plug.save()
    return HttpResponse("success")

# # 특정 구간 내 Sensor의 값을 얻기 위한 view
# def sensor_values_by_time(request, sensor_id):
#     sensor = get_object_or_404(Sensor, pk=sensor_id)
    
#     # 어제의 0시부터 24시까지의 구간
#     start_time = now() - timedelta(days=1)
#     start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
#     end_time = start_time.replace(hour=23, minute=59, second=59, microsecond=999999)
    
#     sensor_values = Sensor_value.objects.filter(sensor=sensor, timestamp__range=(start_time, end_time)).order_by('timestamp')

#     data = {
#         'sensor_name': sensor.name,
#         'start_time': start_time,
#         'end_time': end_time,
#         'sensor_values': [
#             {
#                 'value_type': value.value_type,
#                 'value': value.value,
#                 'timestamp': value.timestamp
#             } for value in sensor_values
#         ]
#     }
#     return JsonResponse(data)



# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .models import Sensor_value
# from .serializers import SensorValueSerializer

# class SensorValueList(APIView):
#     def get(self, request):
#         sensor_values = Sensor_value.objects.all()
#         serializer = SensorValueSerializer(sensor_values, many=True)
#         return Response(serializer.data)
























from .tasks import create_daily_file

def sensor_create_file(request):
    try:
        create_daily_file()
    except:
        pass
    return HttpResponse("Success")



