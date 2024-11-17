from pydantic import BaseModel, Field, field_validator
from typing import Dict, Annotated
from datetime import date as DateType  # Avoid conflict with the variable name
from datetime import datetime
from fastapi import HTTPException, status

class BookingCreate(BaseModel):
    topic_id: Annotated[int, Field(gt=0, example=1)]  # Positive integer
    student_id: Annotated[int, Field(gt=0, example=1)]  # Positive integer
    ta_id: Annotated[int, Field(gt=0, example=4)]  # Positive integer
    date: Annotated[DateType, Field(..., example="2024-11-20")]  # Date in YYYY-MM-DD format
    timeslot: Dict[str, str] = Field(
        ...,
        example={"from": "09:00", "to": "10:00"},
        description="Time should be a dictionary with 'from' and 'to' keys."
    )

    @field_validator("timeslot")
    def validate_timeslot(cls, value: Dict[str, str]):
        # Ensure "from" and "to" keys are present
        if 'from' not in value or 'to' not in value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status":"fail",
                    "message":"Timeslot must contain 'from' and 'to' keys."
                }
            )

        try:
            # Parse times to ensure validity in 12-hour format with AM/PM
            from_time = datetime.strptime(value['from'], "%I:%M %p")
            to_time = datetime.strptime(value['to'], "%I:%M %p")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status":"fail",
                    "message":"Invalid time format. Use HH:MM AM/PM format."
                }
            )
            

        # Check if 'from' is before 'to'
        if from_time >= to_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status":"fail",
                    "message":"'from' time must be earlier than 'to' time."
                }
            )

        return value

    class Config:
        orm_mode = True
        from_attributes = True





class BookingRead(BaseModel):
    id: int = Field(..., example=1)
    topic_id: int = Field(..., example=101)
    student_id: int = Field(..., example=202)
    ta_id: int = Field(..., example=303)
    status: str = Field(..., example="pending")
    date: str
    timeslot: Dict[str, str] = Field(
        ..., example={"from": "09:00", "to": "10:00"}
    )  # Represents {"from": <start_time>, "to": <end_time>}

    class Config:
        orm_mode = True
        from_attributes = True