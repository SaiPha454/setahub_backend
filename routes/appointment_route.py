from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.responses import JSONResponse
from database_connection import get_db
from sqlalchemy.orm import Session
from schemas.appointment_schema import AppointmentCreate,AppointmentUpdate

from services import appointment_service


router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={404: {"description": "Not found"}},
)


# Create a new Appointment
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate, db: Session = Depends(get_db)
):
    

    result = await appointment_service.create_appointment_service(db, appointment_data)
    
    return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status":"success",
                "data":result
            }
        )


@router.get("/{appointment_id}", response_model=dict)
async def get_ta_session_by_id(appointment_id: int, db: Session=Depends(get_db)):
    result = await appointment_service.get_appointment_by_id_service(db, appointment_id)
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status":"success",
                "data":result
            }
        )


@router.put("/{appointment_id}", response_model=dict)
async def update_ta_session(appointment_id: int, appointment_data: AppointmentUpdate , db: Session=Depends(get_db)):
    result = await appointment_service.update_appointment_service(db, appointment_id, appointment_data)
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status":"success",
                "data":result
            }
        )


@router.delete("/{appointment_id}", response_model=dict)
async def delete_ta_session(appointment_id: int, db: Session = Depends(get_db)):
    await appointment_service.delete_appointment_service(db, appointment_id)
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status":"success"
            }
        )