from django.contrib import admin
from django.urls import path

from . import views
urlpatterns = [
    path('start', views.receive_mqtt, name='receive_mqtt'),
    path('stop', views.stop_receiving_mqtt, name='stop_receiving_mqtt')
]