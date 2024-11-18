from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, or_, and_, Enum, ForeignKey
from database_connection import Base
from sqlalchemy.orm import Session, relationship, joinedload
from fastapi import HTTPException, status
import enum



class Message(Base):
    __tablename__ = 'messages'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Sender ID
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Receiver ID
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content (text or URL)
    message = Column(String, nullable=False)
    
    # Timestamp of when the message was sent
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String, default ="sent" , nullable = False)
    # Message type (text or image URL)
    type = Column(String, nullable=False)
    
    from_user = relationship("User", back_populates="sent_messages", foreign_keys=[from_user_id])
    to_user = relationship("User", back_populates="received_messages", foreign_keys=[to_user_id])

    def __repr__(self):
        return f"<Message(from_user_id={self.from_user_id}, to_user_id={self.to_user_id}, message={self.message}, timestamp={self.timestamp},type={self.type})>"


async def create_message_model(db: Session, from_user_id: int, to_user_id: int, message: str, msg_type : str, status : str ):
    new_message =Message(
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        timestamp= datetime.now(timezone.utc),
        status= status,
        message=message,
        type= msg_type
    )
    
    db.add(new_message)
    db.commit()  # Commit the transaction to the database
    db.refresh(new_message)
    return new_message  # Return the added message

async def get_messages_model(db: Session, from_user_id: int, to_user_id: int):

    messages = db.query(Message).filter(
        or_(
            and_(Message.from_user_id == from_user_id, Message.to_user_id == to_user_id),
            and_(Message.from_user_id == to_user_id, Message.to_user_id == from_user_id)
        )
    ).order_by(Message.timestamp.asc()).all()
    return messages


async def get_unread_messages_model(db: Session, user_id: int):
    messages = db.query(Message).options(
        joinedload(Message.from_user),
        joinedload(Message.to_user)
    ).filter(
        Message.to_user_id == user_id, Message.status == "sent"
    ).order_by(Message.timestamp.asc()).all()
    return messages

# async def update_message_status_model(db: Session, message_id: int):
#     message = db.query(Message).filter_by(Message.id == message_id).first()

#     if not message:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={
#                 "status":"fail",
#                 "message":f"The message with ID {message_id} does not exist"
#             }
#         )

#     message.status = MessageStatusEnum.SENT

#     db.commit()  # Commit the changes to the database
#     db.refresh(message)
#     return message  # Return the updated message
