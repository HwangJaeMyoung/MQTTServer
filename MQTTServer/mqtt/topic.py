from .models import SENSOR_TYPE_VALUES

class SensorTopic:
    REGISTER = "Register"
    CONFIRM = "Confirm"
    NOTHING = "Nothing"
    ICCMS  = "ICCMS"
    __SENSOR_TYPE_LEVEL = 5

    @staticmethod
    def init_from_list(sensor_data:list):
        sensor_data.insert(0,SensorTopic.ICCMS)
        sensor_data.append(SensorTopic.NOTHING)
        return SensorTopic('/'.join(sensor_data))

    def __init__(self,topic:str) -> None:
        if topic == None:raise "null"

        self.__topic_per_level=topic.split("/")
        self.__topic = topic

    def isRegister(self):
        return self.__topic_per_level == SensorTopic.REGISTER
    
    def separate(self):
        return self.__topic_per_level[1:-1],self.__topic_per_level[-1]

    def confirm(self):
        separated_confirm_topic=self.separate()[0].append(SensorTopic.CONFIRM)
        return SensorTopic('/'.join(separated_confirm_topic))
    
    def collect(self):
        sensor_type = self.__topic_per_level[SensorTopic.__SENSOR_TYPE_LEVEL]
        collect_topics = []
        for value_type in SENSOR_TYPE_VALUES[sensor_type]:
            separated_collect_topic =  self.separate()[0].append(value_type)
            collect_topics.append(SensorTopic('/'.join(separated_collect_topic)))
        return collect_topics
    
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