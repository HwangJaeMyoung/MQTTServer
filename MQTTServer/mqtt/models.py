from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime
from django.db.models import UniqueConstraint
import logging
from .topic import Sensor_topic
from django.db import transaction, IntegrityError

logger = logging.getLogger("mqtt")

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
       
        try:
            sensor_data_list = [Sensor_value(sensor=self,
                                        device = self.attached_device,
                                        timestamp=datetime.strptime(item['time'], '%Y_%m_%d-%H_%M_%S.%f'),
                                        value=item['value'][property],value_type = property) for property in properties  for item in data ]
            Sensor_value.objects.bulk_create(sensor_data_list,  ignore_conflicts=True)
            return True
        except:
            logging.warning(f"excute create_sensor_value create_error")
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
        topic_object = Sensor_topic(self.topic)
        return topic_object.confirm().__str__()
    
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
    
def set_network(topic:str):
    network= select_network(topic)
    if not network:
        topic_object = Sensor_topic(topic)
        if not topic_object.is_action_type: 
            logger.warning(f"excute set_network() wrong topic_object.is_action_type:{topic_object.action_type}")
            try:
                network, created = Sensor_networking.objects.get_or_create(
                    topic=topic,
                    defaults={'direction': True, 'status': False}
                )
            except IntegrityError:
                network = Sensor_networking.objects.get(topic=topic)
            return network
        
        sensor = select_sensor(topic_object.body())

        if not sensor or not sensor.attention: 
            logger.warning(f"excute set_network() sensor:{sensor} or sensor.attention is False")
            try:
                network, created = Sensor_networking.objects.get_or_create(
                    topic=topic,
                    defaults={'direction': True, 'status': False}
                )
            except IntegrityError:
                network = Sensor_networking.objects.get(topic=topic)
            return network
        logger.debug(f"excute set_network() Register")
        try:
            with transaction.atomic():
                if topic_object.action_type == Sensor_topic.REGISTER:
                    network, created = Sensor_networking.objects.get_or_create(sensor = sensor,
                                                    device =sensor.collecting_device,
                                                    topic= topic,
                                                    action_type = Sensor_topic.REGISTER,
                                                    direction = True,
                                                    status = True)
                    if created:
                        confirm_network, created = Sensor_networking.objects.get_or_create(topic= topic_object.confirm())
                        confirm_network.sensor = sensor
                        confirm_network.device =sensor.collecting_device
                        confirm_network.topic= topic_object.confirm()
                        confirm_network.action_type = Sensor_topic.CONFIRM
                        confirm_network.direction = False
                        confirm_network.status =True
                        confirm_network.save()

                        value_network, created = Sensor_networking.objects.get_or_create(topic= topic_object.value())
                        value_network.sensor = sensor
                        value_network.device =sensor.collecting_device
                        value_network.action_type = Sensor_topic.VALUE
                        value_network.direction = True
                        value_network.status = True
                        value_network.save()
                    logger.debug(f"excute set_network() Register success")
                else:
                    logger.warning(f"excute set_network() not regeisted network")
                    network, created = Sensor_networking.objects.get_or_create(
                        topic=topic,
                        defaults={'direction': True, 'status': False}
                    )
        except IntegrityError as e:
            logger.error(f"excute set_network() error: {str(e)}")
            try:
                network = Sensor_networking.objects.get(topic=topic)
            except Sensor_networking.DoesNotExist:
                network, created = Sensor_networking.objects.get_or_create(
                    topic=topic,
                    defaults={'direction': True, 'status': False}
                )
    return network

