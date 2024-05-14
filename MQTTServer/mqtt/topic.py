
class SensorTopic:
    REGISTER = "Register"
    CONFIRM = "Confirm"
    NOTHING = "Nothing"
    VALUE = "X"
    ICCMS  = "ICCMS"

    @staticmethod
    def init_from_sensor(sensor_name:str):
        sensor_data=sensor_name.split("/")
        sensor_data.insert(0,SensorTopic.ICCMS)
        sensor_data.append(SensorTopic.NOTHING)
        return SensorTopic('/'.join(sensor_data))

    def __init__(self,topic:str) -> None:
        if topic == None:raise "null"

        self.__topic_per_level=topic.split("/")
        self.__topic = topic

    def isRegister(self):
        return self.__topic_per_level[-1] == SensorTopic.REGISTER
    
    def separate(self):
        return self.__topic_per_level[1:-1],self.__topic_per_level[-1]

    def confirm(self):
        separated_confirm_topic=self.separate()[0]
        separated_confirm_topic.append(SensorTopic.CONFIRM)
        separated_confirm_topic.insert(0,SensorTopic.ICCMS)
        return SensorTopic('/'.join(separated_confirm_topic))
    
    def value(self):
        separated_value_topic = self.separate()[0]
        separated_value_topic.append(SensorTopic.VALUE)
        separated_value_topic.insert(0,SensorTopic.ICCMS)
        return SensorTopic('/'.join(separated_value_topic))
    
    def __getitem__(self, index):
        return self.__topic_per_level[index]
    
    def __str__(self) -> str:
        return self.__topic
    

REGISTER_TOPIC = SensorTopic("ICCMS/+/+/+/+/+/Register")

if __name__ == "__main__":
    print(REGISTER_TOPIC)
    for i in REGISTER_TOPIC:
        print(i)
    print(REGISTER_TOPIC.separate())