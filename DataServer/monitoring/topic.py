class Sensor_topic:
    REGISTER = "Register"
    CONFIRM = "Confirm"
    VALUE = "Value"
    ICCMS  = "ICCMS"
    ACTION_TYPE=[REGISTER,CONFIRM,VALUE]
    
    def __init__(self,topic:str) -> None:
        if topic == None:raise "null"
        self.__topic_per_level=topic.split("/")
        self.__topic = topic
        if self.__topic_per_level[-1] in Sensor_topic.ACTION_TYPE:
            self.action_type = self.__topic_per_level[-1]
            self.is_action_type= True
        else:
            self.action_type = self.__topic_per_level[-1]
            self.is_action_type = False

    def body(self):
        return self.__topic_per_level[1:-1]

    def confirm(self):
        separated_confirm_topic=self.body()
        separated_confirm_topic.append(Sensor_topic.CONFIRM)
        separated_confirm_topic.insert(0,Sensor_topic.ICCMS)
        return Sensor_topic('/'.join(separated_confirm_topic))
    
    def value(self):
        separated_confirm_topic=self.body()
        separated_confirm_topic.append(Sensor_topic.VALUE)
        separated_confirm_topic.insert(0,Sensor_topic.ICCMS)
        return Sensor_topic('/'.join(separated_confirm_topic))
    

    def __getitem__(self, index):
        return self.__topic_per_level[index]
    
    def __str__(self) -> str:
        return self.__topic