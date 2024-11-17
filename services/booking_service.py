from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from schemas.booking_schema import BookingCreate, BookingRead
from models import booking_model, topics_model, users_model
from schemas.booking_detail_schema import BookingDetailRead
from schemas.user_with_session_schema import UserReadWithTASession
from .user_service import get_user_available_timeslots_service

async def create_booking_service(db: Session, booking: BookingCreate):
    
    existing_booking = await booking_model.already_booked(db, booking_data=booking)
    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "fail", 
                "message": f"Booking already exists for the date {booking.date}."}
        )
    
    topic = topics_model.get_topic_by_id(db, booking.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "fail", 
                "message": "The requested topic does not exist"}
        )
    ta = await users_model.get_user_by_id_with_appointments_model(db, booking.ta_id)
    if not ta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "fail", 
                "message": "The requested TA does not exist"}
        )
    
    available_timeslots = await get_user_available_timeslots_service(db, user_id=booking.ta_id, topic_id=booking.topic_id)
    booking_date = booking.date.strftime("%Y-%m-%d")
    
    if booking_date not in available_timeslots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "fail", 
                "message": "The requested date is not available"}
        )

    if booking.timeslot not in available_timeslots[booking_date] or len(available_timeslots[booking_date]) <=0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "fail", 
                "message": f"Timeslot {booking.timeslot} for {booking_date} is not available"}
        )

    new_booking = await booking_model.create_booking_model(db, booking_data=booking)
    new_booking.date = new_booking.date.strftime("%Y-%m-%d")
    new_booking = BookingRead.model_validate(new_booking).model_dump()
    
    return new_booking


async def get_booking_by_id_service(db: Session, booking_id: int):

    booking = await booking_model.get_booking_by_id_model(db, booking_id)
    booking.date = booking.date.strftime("%Y-%m-%d")
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "fail", 
                "message": "The Booking does not exist"}
        )  
    return BookingDetailRead.model_validate(booking).model_dump()


async def complete_booking_service(db: Session, booking_id: int):

    booking = await booking_model.complete_booking_model(db, booking_id)
    booking.date = booking.date.strftime("%Y-%m-%d")
    return BookingRead.model_validate(booking).model_dump()
    
async def delete_booking_by_id_service(db: Session, booking_id: int):

    deleted_booking = await booking_model.delete_booking_by_id_model(db, booking_id)
    if not deleted_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "fail", 
                "message": "The Booking does not exist"}
        )
    return deleted_booking
