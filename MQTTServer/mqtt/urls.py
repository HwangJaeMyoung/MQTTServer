from django.contrib import admin
from django.urls import path
from . import views

# urlpatterns = [
#     # path('start', views.receive_mqtt, name='receive_mqtt'),
#     # path('stop', views.stop_receiving_mqtt, name='stop_receiving_mqtt')
# ]

urlpatterns = [
    path('', views.sensor_data_list, name='sensor_data_list'),
    path('sensor/<int:pk>/', views.sensor_data_detail, name='sensor_data_detail'),
    path('sensor/new/', views.sensor_data_new, name='sensor_data_new'),
    
#     path('sensor/<int:pk>/edit/', views.sensor_data_edit, name='sensor_data_edit'),
#     path('sensor/<int:pk>/delete/', views.sensor_data_delete, name='sensor_data_delete'),
]