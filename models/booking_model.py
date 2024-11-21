from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Date, JSON, or_, and_
from sqlalchemy.orm import relationship, joinedload
import enum
from sqlalchemy.orm import Session
from schemas.booking_schema import BookingCreate
from database_connection import Base
from fastapi import HTTPException, status
from datetime import date
from sqlalchemy import update

class BookingStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)  # Assuming a topics table exists
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Refers to User model
    ta_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Refers to User model
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    date = Column(Date, nullable=False)
    timeslot = Column(JSON, nullable=False)  # Storing time as a JSON object {"from": "09:00", "to": "10:00"}

    # Relationships
    
    student = relationship("User", foreign_keys=[student_id], back_populates="student_bookings")
    ta = relationship("User", foreign_keys=[ta_id], back_populates="ta_bookings")
    topic = relationship("Topic", back_populates="bookings")  # Assuming a Topic model

    def __repr__(self):
        return f"<Booking(id={self.id}, topic_id={self.topic_id}, student_id={self.student_id}, ta_id={self.ta_id}, status={self.status}, date={self.date}, timeslot={self.timeslot})>"



async def create_booking_model(db: Session, booking_data: BookingCreate):

    new_booking = Booking(
        topic_id=booking_data.topic_id,
        student_id=booking_data.student_id,
        ta_id=booking_data.ta_id,
        status=BookingStatus.PENDING,
        date=booking_data.date,
        timeslot=booking_data.timeslot
    )


    # Add to database
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    topic = await get_booking_by_id_model(db, booking_id=new_booking.id)
    topic = topic.topic
    topic.booked = topic.booked +1
    db.commit()
    db.refresh(topic)

    return new_booking

async def already_booked(db: Session, booking_data: BookingCreate):
    booking = db.query(Booking).filter(
        Booking.topic_id == booking_data.topic_id,
        Booking.student_id == booking_data.student_id,
        Booking.date == booking_data.date,
        # Booking.timeslot == booking_data.timeslot,
        Booking.ta_id == booking_data.ta_id,
        Booking.status == BookingStatus.PENDING
    ).first()
    return booking

async def get_booking_by_id_model(db: Session, booking_id: int):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    return booking



async def get_booking_between_two_users(db: Session, user1_id: int, user2_id: int):
    
    booking = db.query(Booking).filter(
        or_(
            and_(Booking.ta_id == user1_id, Booking.student_id == user2_id, Booking.status==BookingStatus.PENDING),
            and_(Booking.ta_id == user2_id, Booking.student_id == user1_id, Booking.status==BookingStatus.PENDING),
        )
    ).first()
    return booking



async def complete_booking_model(db: Session, booking_id: int):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "fail", 
                "message": "The Booking does not exist"}
        )
    booking.status = BookingStatus.COMPLETED
    db.commit()
    db.refresh(booking)
    return booking



async def get_student_upcoming_bookings_model(db: Session, user_id: int):

    bookings = (
        db.query(Booking)
        .options(
            joinedload(Booking.ta),
            joinedload(Booking.topic)
        )
        .filter(
            Booking.student_id == user_id,
            Booking.status == BookingStatus.PENDING
        ).all()
    )

    return bookings


async def get_student_completed_bookings_model(db: Session, user_id: int):

    bookings = (
        db.query(Booking)
        .options(
            joinedload(Booking.ta),
            joinedload(Booking.topic)
        )
        .filter(
            Booking.student_id == user_id,
            Booking.status == BookingStatus.COMPLETED
        ).all()
    )

    return bookings


async def get_ta_upcoming_appointments_model(db: Session, user_id: int):

    bookings = (
        db.query(Booking)
        .options(
            joinedload(Booking.ta),
            joinedload(Booking.topic)
        )
        .filter(
            Booking.ta_id == user_id,
            Booking.status == BookingStatus.PENDING
        ).all()
    )

    return bookings


async def get_ta_completed_appointments_model(db: Session, user_id: int):

    bookings = (
        db.query(Booking)
        .options(
            joinedload(Booking.ta),
            joinedload(Booking.topic)
        )
        .filter(
            Booking.ta_id == user_id,
            Booking.status == BookingStatus.COMPLETED
        ).all()
    )

    return bookings

async def delete_booking_by_id_model(db: Session, booking_id: int):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        db.delete(booking)
        db.commit()
        return True
    return False



def mark_overdated_bookings_as_completed(session: Session):
    """
    Marks bookings with dates earlier than today as completed.
    This function works with PostgreSQL using SQLAlchemy.
    """
    today = date.today()

    # Update query to mark outdated bookings as completed
    stmt = (
        update(Booking)
        .where(Booking.date < today, Booking.status == BookingStatus.PENDING)
        .values(status=BookingStatus.COMPLETED)
    )
    
    # Execute and commit the transaction
    session.execute(stmt)
    session.commit()
    print("Overdated bookings have been marked as completed.")