from pydantic import BaseModel
from sqlalchemy import Enum
from datetime import datetime
from schemas.user_shema import UserRead

# MessageCreate schema
# class MessageCreate(BaseModel):
#     from_user_id: int
#     to_user_id: int
#     timestamp: datetime
#     message: str
#     type: str

#     class Config:
#         orm_mode = True
#         from_attributes = True

# MessageRead schema
class MessageRead(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    message: str
    timestamp: datetime
    status: str
    type: str
    from_user: UserRead
    to_user: UserRead

    class Config:
        orm_mode = True
        from_attributes = True


class MessageSentData(BaseModel):
    from_user_id: int
    to_user_id: int
    msg_type: str = None
    message: str = None

class MessageSent(BaseModel):
    type: str
    data: MessageSentData