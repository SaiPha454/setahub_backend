from .booking_schema import BookingRead
from .user_shema import UserRead
from .topic_shema import TopicRead

class BookingDetailRead(BookingRead):
    student: UserRead
    ta: UserRead
    topic: TopicRead

class BookingReadWithTopicAndTA(BookingRead):
    ta: UserRead
    topic: TopicRead


class BookingReadWithTopicAndStudent(BookingRead):
    student: UserRead
    topic: TopicRead