"""DataServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from monitoring import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("aa/", views.sensor_create_file, name='sensor_data_new'),
    # path("turn/on/<pk>",views.turn_on_plug_status_view,name= "turn_on_plug")
    # path("turn/off/<pk>", views.turn_off_plug_status_view,name= "turn_off_plug")
]
    # path('', views.sensor_data_list, name='sensor_data_list'),
    # path('sensor/<int:pk>/', views.sensor_data_detail, name='sensor_data_detail'),
    # path('sensor/new/', views.sensor_data_new, name='sensor_data_new'),