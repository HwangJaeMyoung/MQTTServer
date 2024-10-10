class Sensor_topic:
    REGISTER = "Register"
    CONFIRM = "Confirm"
    NOTHING = "Nothing"
    VALUE = "Value"
    ICCMS  = "ICCMS"
    ACTION_TYPE=[REGISTER,CONFIRM,VALUE]
    @staticmethod
    def init_from_sensor(sensor_name:str):
        sensor_data=sensor_name.split("/")
        sensor_data.insert(0,Sensor_topic.ICCMS)
        sensor_data.append(Sensor_topic.NOTHING)
        return Sensor_topic('/'.join(sensor_data))

    def __init__(self,topic:str) -> None:
        if topic == None:raise "null"
        self.__topic_per_level=topic.split("/")
        self.__topic = topic
        if self.__topic_per_level[-1] in Sensor_topic.ACTION_TYPE:
            self.action_type = self.__topic_per_level[-1]
        else:
            self.action_type = "Other"

    def isRegister(self):
        return self.__topic_per_level[-1] == Sensor_topic.REGISTER
    
    def separate(self):
        return self.__topic_per_level[1:-1],self.__topic_per_level[-1]

    def confirm(self):
        separated_confirm_topic=self.separate()[0]
        separated_confirm_topic.append(Sensor_topic.CONFIRM)
        separated_confirm_topic.insert(0,Sensor_topic.ICCMS)
        return Sensor_topic('/'.join(separated_confirm_topic))
    
    def value(self):
        separated_value_topic = self.separate()[0]
        separated_value_topic.append(Sensor_topic.VALUE)
        separated_value_topic.insert(0,Sensor_topic.ICCMS)
        return Sensor_topic('/'.join(separated_value_topic))
    
    def __getitem__(self, index):
        return self.__topic_per_level[index]
    
    def __str__(self) -> str:
        return self.__topic
    
REGISTER_TOPIC = Sensor_topic("ICCMS/+/+/+/+/+/Register")

if __name__ == "__main__":
    print(REGISTER_TOPIC)
    for i in REGISTER_TOPIC:
        print(i)
    print(REGISTER_TOPIC.separate())