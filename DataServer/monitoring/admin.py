from django.contrib import admin
from .models import Location, Plug_type, Plug, Device_type, Device, Sensor_type, Sensor

# Location 모델 관리자 설정
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

# Plug_type 모델 관리자 설정
class PlugTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'model', 'wifi', 'admin_email')
    search_fields = ('name', 'model')
    list_filter = ('wifi',)

# Plug 모델 관리자 설정
class PlugAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'plug_type', 'status', 'created_at')
    search_fields = ('name',)
    list_filter = ('location', 'plug_type', 'status')

# Device_type 모델 관리자 설정
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'model', 'wifi', 'created_at')
    search_fields = ('name', 'model')
    list_filter = ('wifi',)

# Device 모델 관리자 설정
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'device_type', 'status', 'created_at')
    search_fields = ('name',)
    list_filter = ('location', 'device_type', 'status')

# Sensor_type 모델 관리자 설정
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'model', 'properties')
    search_fields = ('name',)
    list_filter = ('name',)

# Sensor 모델 관리자 설정
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sensor_type', 'AttachedDevice', 'CollectingDevice', 'status')
    search_fields = ('name',)
    list_filter = ('sensor_type', 'status')

# 모델 등록
admin.site.register(Location, LocationAdmin)
admin.site.register(Plug_type, PlugTypeAdmin)
admin.site.register(Plug, PlugAdmin)
admin.site.register(Device_type, DeviceTypeAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Sensor_type, SensorTypeAdmin)
admin.site.register(Sensor, SensorAdmin)
