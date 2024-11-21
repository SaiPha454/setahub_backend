from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.topics_model import get_topic_by_id
from models.users_model import get_user_by_id
# from models.tasession_model import create_ta_session_model, get_ta_session_by_topic_id_and_ta_id_model, get_ta_session_by_id_model, delete_ta_session_model
from models import appointment_model
from schemas.appointment_schema import AppointmentCreate, AppointmentRead, AppointmentUpdate
from schemas.appointment_detail_schema import AppointmentReadWithTopicAndTA


async def create_appointment_service(db: Session, data: AppointmentCreate)->AppointmentRead:

    topic =  get_topic_by_id(db,data.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":f"The topic with ID {data.topic_id} does not exist"
            }
        )
    user = await get_user_by_id(db, data.ta_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":f"The user with ID {data.ta_id} does not exist"
            }
        )
    
    already_exist = await appointment_model.get_appointment_by_topic_id_and_ta_id_model(db, data.topic_id,data.ta_id)
    if already_exist != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"The user already register for this topic"
            }
        )
    
    topic.tas = topic.tas +1
    db.commit()
    db.refresh(topic)
    appointment = await appointment_model.create_appointment_model(db,data=data)
    appointment = AppointmentRead.model_validate(appointment)
    return AppointmentRead.model_dump(appointment)


async def get_appointment_by_id_service(db: Session, appointment_id: int):
    
    result = await appointment_model.get_appointment_by_id_model(db=db, appointment_id=appointment_id)
    
    result = AppointmentReadWithTopicAndTA.model_validate(result).model_dump()
    return result 


async def get_appointment_by_topic_and_ta_service(db: Session, topic_id: int, ta_id: int):
    
    result = await appointment_model.get_appointment_by_topic_id_and_ta_id_model(db=db, topic_id=topic_id, ta_id=ta_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status":"fail",
                "message":f"The appointment with topic id {topic_id} and ta_id {ta_id} does not exist"
            }
        )
    result = AppointmentReadWithTopicAndTA.model_validate(result).model_dump()
    return result 


async def update_appointment_service(db: Session, appointment_id:int, appointment: AppointmentUpdate):
    
    result = await appointment_model.update_appointment_model(
        db, 
        appointment_id=appointment_id, 
        date=appointment.date,
        timeslots=appointment.timeslots
    )
    
    return AppointmentRead.model_validate(result).model_dump()



async def delete_appointment_service(db: Session, appointment_id: int):

    appointment = await appointment_model.get_appointment_by_id_model(db, appointment_id)
    
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":f"The Appointment with ID {appointment_id} does not exist"
            }
        )
    return await appointment_model.delete_appointment_model(db, appointment_id)


    