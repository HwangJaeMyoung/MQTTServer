from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

@receiver(post_save, sender=Sensor)
def send_mqtt_command(sender, instance, **kwargs):
    if kwargs['created']:  # 새로운 인스턴스 생성 시에만 동작하도록
        mqtt_client = apps.get_app_config('mqtt').mqtt_client
        mqtt_message = "unsubscribe {}"  # MQTT 메시지를 구독 취소 명령으로 설정
        mqtt_message = mqtt_message.format(instance.value)  # 모델의 값으로 메시지를 채움
        mqtt_client.publish("topic", mqtt_message)  # MQTT 클라이언트로 메시지 전송