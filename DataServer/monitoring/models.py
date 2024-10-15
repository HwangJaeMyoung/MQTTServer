from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime
import csv 
from io import StringIO 
from PyP100 import PyP100
from django.db.models import UniqueConstraint
import logging
from .topic import Sensor_topic

logger = logging.getLogger("monitor")

class Location(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'location'

    def __str__(self):
        return self.name
    def select(self,name:str):
        try:
            location = self.child.get(name=name)
            return location
        except Location.DoesNotExist:
            try:
                device =self.device_set.get(name=name)
                return device
            except Device.DoesNotExist:
                logger.warning(f"excute select() not exist location or device matched name: {name}")
                return False
        
class Plug_type(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100,null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    wifi = models.BooleanField(default=False)
    admin_email = models.EmailField(max_length=100,default="DT.TUKOREA@gmail.com",null=True, blank=True) 
    admin_passwd = models.CharField(max_length=100,default="DiK_WiMiS_30!", null=True, blank=True)

    class Meta:
        db_table = 'plug_type'

    def login_admin(self,ip_address):
        logger.debug(f"excute login_admin()")
        try:
            if self.model.lower() == "p100":
                logger.debug(f"excute login_admin() case p100")
                p100 = PyP100.P100(str(ip_address), self.admin_email, self.admin_passwd)
                p100.handshake()  
                p100.login()
                return p100
            else: return False
        except:
            logger.warning(f"excute login_admin() error handshake")
            return False 
    def get_status(self,ip_address):
        if self.login_admin(ip_address):return True
        else: return False
    def turn_off_plug(self,ip_address):
        try:
            plug = self.login_admin(ip_address)
            if not plug : return False
            if self.model == "p100":
                plug.turnOff()
                return True
            else: return False
        except:
            return False

    def turn_on_plug(self,ip_address):
        try:
            plug = self.login_admin(ip_address)
            if not plug : return False
        
            if self.model == "p100":
                plug.turnOn()
                return True
            else: return False
        except:
            return False
        
    def get_plug_status(self,ip_address):
        try:
            plug = self.login_admin(ip_address)
            if not plug : return False
            if self.model == "p100":
                plug_status = plug.getDeviceInfo()["device_on"]
                return plug_status
            else: return False
        except:
            return False

class Plug(models.Model):
    location = models.ForeignKey(Location,on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)

    plug_type=  models.OneToOneField(Plug_type,on_delete=models.SET_NULL, null=True, blank=True)

    attention = models.BooleanField(default=False)
    
    status = models.BooleanField(default=False)
    target_status = models.BooleanField(default=False)

    plug_status = models.BooleanField(default=False)
    target_plug_status = models.BooleanField(default=False)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'plug'

    def __str__(self):
        return self.name

    def set_status(self):
        if self.plug_type.wifi == False: return False
        status = self.plug_type.get_status(self.ip_address)
        if self.status != status: 
            self.status = status
            self.save()
        if self.target_status == True and self.status == False:return False
        return True
    
    def set_plug_status(self):
        if self.plug_type.wifi == False: return False
        plug_status = self.plug_type.get_plug_status(self.ip_address)
        if self.plug_status != plug_status: 
            self.plug_status = plug_status
            self.save()
        if self.plug_status == self.target_plug_status: return True

        if self.target_plug_status:
            result = self.plug_type.turn_on_plug(self.ip_address)
        else:
            result = self.plug_type.turn_off_plug(self.ip_address)
            
        if result == False:return False
        self.plug_status = self.target_plug_status
        self.save()
        return True
    
class Device_type(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100,null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    wifi = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device_type'

    def get_status(self,ip_address):
        if self.model == "esp32":
            pass
        return True

class Device(models.Model):
    location = models.ForeignKey(Location,on_delete=models.SET_NULL, null=True, blank=True)
    
    plug = models.ForeignKey(Plug,on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')

    name = models.CharField(max_length=100)
    device_type= models.OneToOneField(Device_type,on_delete=models.SET_NULL, null=True, blank=True)

    attention = models.BooleanField(default=False)
    target_status = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device'

    def __str__(self):
        return self.name
    
    def set_status(self):
        if self.device_type.wifi == False: return False
        status = self.device_type.get_status(self.ip_address)
        if self.state != status: 
            self.status = status
            self.save()
        if self.target_state == True and self.status == False:return False
        return True

    def select(self,name:str):
        try:
            device =self.child.get(name=name)
            return device
        except Device.DoesNotExist:
            try:
                sensor =self.attached_sensors.get(name=name)
                return sensor
            except Sensor.DoesNotExist:
                logger.warning(f"excute select() not exist  device or sensor matched name: {name}")
                return False
    def get_locations(self):
        locations = []
        current_device = self
        while current_device:
            locations.append(current_device.name)
            if current_device.parent:
                current_device = current_device.parent
            elif isinstance(current_device,Device):
                current_device = current_device.location
            else:
                current_device = current_device.parent
        return "_".join(locations[::-1])

class Sensor_type(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=50, blank=True, null=True)    
    properties = models.JSONField(default=list, blank=True, null=True)  

    class Meta:
        db_table = 'sensor_type'

    def save(self, *args, **kwargs):
        if not self.properties:
            if self.name == "Vibration":
                self.properties = ["x", "y", "z"]
            elif self.name == "Temperature":
                self.properties = ["Temperature"]
            elif self.name == "Humidity":
                self.properties = ["Humidity"]
            elif self.name == "Current":
                self.properties = ["Current"]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    attached_device = models.ForeignKey(Device,on_delete=models.SET_NULL, null=True, blank=True,related_name='attached_sensors')
    collecting_device= models.ForeignKey(Device,on_delete=models.SET_NULL, null=True, blank=True,related_name='collecting_sensors')
    name = models.CharField(max_length=100)
    sensor_type = models.OneToOneField(Sensor_type,on_delete=models.SET_NULL,null=True, blank=True)
    attention = models.BooleanField(default=False)

    class Meta:
        db_table = 'sensor'

    def __str__(self):
        return self.name
    
    def check_attention(self):
        if self.attached_device != None and not self.attached_device.attention: return False
        if self.collecting_device != None and not self.collecting_device.attention: return False
        return self.attention
    
    def create_sensor_value(self,data:list):
        for item in data:
            key = item["value"].keys()
            if list(key) !=self.sensor_type.properties:
                logging.warning(f"excute create_sensorValue porperty not match {key}:{self.sensor_type.properties}")
                return False
        properties = self.sensor_type.properties
        sensor_data_list = [Sensor_value(sensor=self,
                                        device = self.attached_device,
                                        timestamp=datetime.strptime(item['time'], '%Y_%m_%d-%H_%M_%S.%f'),
                                        value=item['value'][property],value_type = property) for property in properties  for item in data ]
        try:
            Sensor_value.objects.bulk_create(sensor_data_list,  ignore_conflicts=True)
            return True
        except:
            logging.warning(f"excute create_sensor_value bulk_create_error")
            return False

class Sensor_networking(models.Model):
    sensor=models.ForeignKey(Sensor,on_delete=models.CASCADE, null=True, blank=True,)
    device=models.ForeignKey(Device,on_delete=models.CASCADE, null=True, blank=True,)

    topic = models.CharField(max_length=100,primary_key=True)
    action_type = models.CharField(max_length=15,null=True, blank=True, choices=[(Sensor_topic.REGISTER, "Register"), (Sensor_topic.CONFIRM, "Confirm"), (Sensor_topic.VALUE, "Value")])
    
    direction = models.BooleanField(default=True)  # True: Received, False: Sent
    status = models.BooleanField(default=False)
    network_status= models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True,blank=True)

    class Meta:
        db_table = 'sensor_networking'
    
    def run(self):
        self.timestamp= timezone.now()
        self.network_status = True
        if self.status == False: return False
        self.save()
        return True
    
    def confirm(self):
        return Sensor_topic(self.topic).confirm().__topic
    
    def set_network_status(self,status):
        self.network_status= status
        self.save()
        return 
    
class Sensor_value(models.Model):
    sensor =  models.ForeignKey(Sensor, on_delete=models.CASCADE,db_index=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE,db_index=True)
    value_type = models.CharField(max_length=255)
    value = models.FloatField()
    timestamp= models.DateTimeField(null=True,blank=True)
    class Meta:
        
        db_table = 'sensor_value'

        indexes = [
            models.Index(fields=['sensor_id',"timestamp","value_type"]),
        ]
        constraints = [
            UniqueConstraint(fields=['sensor', 'timestamp', 'value_type'], name='unique_sensor_timestamp'),
        ]

class Sensor_value_file(models.Model):
    device = models.ForeignKey(Device, on_delete=models.SET_NULL,null=True,blank=True)
    sensor =  models.ForeignKey(Sensor, on_delete=models.SET_NULL,null=True,blank=True)
    value_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    file = models.FileField(upload_to="data/",max_length=200)

    class Meta:
        db_table = 'sensor_value_file'

    def setfile(self,file_content):
        self.file.save(self.get_file_name(),ContentFile(file_content))

    def get_file_name(self):
        filename_sensor =  f'{self.device.get_locations()}_{self.sensor.sensor_type.name}'        
        filename_day = f'/{self.timestamp.year:04}_{self.timestamp.month:02}_{self.timestamp.day:02}'
        filename= f"{filename_sensor}/{filename_day}_raw_{self.value_type}/{filename_day}_timeraw_{self.value_type.lower()}.csv"
        return filename

def select(name:str):
    try:
        location = Location.objects.get(name=name)
        if not location.parent == None:return False
        return location
    except Location.DoesNotExist:
        try:
            device = Device.objects.get(name=name)
            if not device.parent == None or not device.location == None:return False
            return device
        except Device.DoesNotExist:
            logger.warning(f"excute select() not exist location or device matched name: {name}")
            return False
    
def select_sensor(data:list):
    selected_object = select(data[0])
    if not selected_object:return False
    for name in data[1:]:
        selected_object = selected_object.select(name)
        if not selected_object: return False
    if isinstance(selected_object, Sensor):
        return selected_object
    else:
        logger.warning(f"excute selectSensor() not sensor: {selected_object}")
        return False 

def select_network(topic:str):
    try:
        network = Sensor_networking.objects.get(topic = topic)
        return network
    except Sensor_networking.DoesNotExist:
        logger.warning(f"excute select_network() not exist sensor_network matched topic:{topic}")
        return False

def create_sensor_value_file(sensor:Sensor):
    for properties in sensor.sensor_type.properties:
        sensor_value_list= sensor.sensor_value_set.filter(value_type =properties)
        sensorValue_count = len(sensor_value_list)
        if sensorValue_count == 0: return
        sensorValue_time_value_list =  sensor_value_list.order_by("timestamp").values_list("timestamp","value")
        csv_data = StringIO()
        csv_data.write(u'\ufeff')
        writer = csv.writer(csv_data)
        writer.writerow(["",'Time_[s]', "Acceleration[g]"])
        for i, value in enumerate(sensorValue_time_value_list):
            time = (value[0] - sensorValue_time_value_list[0][0]).seconds
            writer.writerow([i,time,value[1]])
        file_content = csv_data.getvalue().encode("utf-8")
        sensorValueFile= Sensor_value_file(sensor=sensor,device=sensor.attached_device,value_type=properties,timestamp = timezone.now())
        sensorValueFile.setfile(file_content)
        sensorValueFile.save()

        for sensorValue in sensor_value_list:
            sensorValue.delete()