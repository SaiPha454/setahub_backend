from .appointment_schema import AppointmentRead
from .user_shema import UserRead
from .topic_shema import TopicRead



class AppointmentReadWithTopicAndTA(AppointmentRead):
    ta: UserRead
    topic: TopicRead