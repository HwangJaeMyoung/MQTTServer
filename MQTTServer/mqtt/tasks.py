from datetime import datetime
from .client import start_maintenance, end_maintenance
from .models import Sensor_value

def scheduled_task():
    start_maintenance()
    #등록된 스마트 플러그에게 정지 명령을 내림
    #모든 센서의 데이터를 csv_로 변환하는 함수
    #시간이 지난 후 등록된 플러그에게 재시작 명령을 내림
    end_maintenance()




