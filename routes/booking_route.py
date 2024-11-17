from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.responses import JSONResponse
from database_connection import get_db
from sqlalchemy.orm import Session
from schemas.booking_schema import BookingCreate
from services import booking_service

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=dict)
async def create_booking(booking: BookingCreate, db: Session=Depends(get_db) ):
    
    result = await booking_service.create_booking_service(db, booking)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data":result
        }
    )

@router.get("/{booking_id}", response_model=dict)
async def get_booking_by_id(booking_id: int, db: Session =Depends(get_db)):
    result = await booking_service.get_booking_by_id_service(db, booking_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data":result
        }
    )

@router.put("/{booking_id}", response_model=dict)
async def complete_booking(booking_id: int, db: Session= Depends(get_db)):
    
    result = await booking_service.complete_booking_service(db, booking_id)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"scuccess",
            "data":result
        }
    )

@router.delete("/{booking_id}", response_model=dict)
async def delete_booking_by_id(booking_id: int, db: Session =Depends(get_db)):
    result = await booking_service.delete_booking_by_id_service(db, booking_id)
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status":"success"
            }
        )