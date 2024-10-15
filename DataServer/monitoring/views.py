from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
from .tasks import create_daily_file

def sensor_create_file(request):
    try:
        create_daily_file()
    except:
        pass
    return HttpResponse("Success")