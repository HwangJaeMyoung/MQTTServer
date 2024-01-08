
MAX_VALUE_NUM = 4096
# MAX_VALUE_NUM = 1


VALUE_TYPE_LIST = ["X","Y","Z","Temperature","Humidity","Current"]

SENSOR_TYPE_DICT = {
    0:"Vibration",
    1:"Temperature",
    2:"Humidity",
    3:"TemperatureHumidity",
    4:"Current",
    "Vibration" :0,
    "Temperature":1,
    "Humidity":2,
    "TemperatureHumidity":3,
    "Current": 4
}

SENSOR_VALUE_MAP_DICT = {
    "Vibration" :["X","Y","Z"],
    "Temperature":["Temperature"],
    "Humidity":["Humidity"],
    "TemperatureHumidity":["Temperature","Humidity"],
    "Current":["Current"]
}