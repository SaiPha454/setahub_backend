
from pydantic import BaseModel, field_validator, FieldValidationInfo

from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status

class AppointmentRead(BaseModel):
    id: int
    topic_id:int
    ta_id: int
    date: List[str]
    timeslots: Optional[dict] = None 

    class Config:
        orm_mode = True
        from_attributes = True



        
class AppointmentCreate(BaseModel):
    topic_id: int
    ta_id: int
    date: Optional[List[str]] = None  # Optional date field (e.g., "2024-11-15")
    timeslots: Optional[dict] = None  # List of dictionaries, each with time and label

    class Config:
        orm_mode = True  # Enable ORM mode so that Pydantic will work with SQLAlchemy models
        from_attributes = True

        # Validator to check that each date string is in the correct format
    @field_validator("date")
    def validate_dates(cls, v):
        
        if v:
            # Ensure each date string is in "YYYY-MM-DD" format
            for date_str in v:
                try:
                    # Attempt to parse each date string using the desired format
                    datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status":"fail",
                            "message":f"Invalid date format {date_str}"
                        }
                    )
        return v
    # Validator for `timeslots` field
    @field_validator("timeslots")
    def validate_timeslots(cls, v, info: FieldValidationInfo):
        dates = info.data.get("date")
        if dates is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "fail",
                    "message": "The `date` field is required for validating `timeslots`."
                }
            )

        # Check if all dates in `date` appear as keys in `timeslots`
        missing_dates = [d for d in dates if d not in v]
        if missing_dates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "fail",
                    "message": f"Missing timeslots for dates: {', '.join(missing_dates)}"
                }
            )
        
        # Validate timeslot structure and content
        for date_key, slots in v.items():
            if date_key not in dates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "fail",
                        "message": f"Unexpected date {date_key} in timeslots."
                    }
                )
            try:
                datetime.strptime(date_key, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "fail",
                        "message": f"Invalid date format in timeslots key: {date_key}"
                    }
                )
            
            if type(slots) != list:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "fail",
                        "message": f"Timeslots for {date_key} should be list of dict"
                    }
                )

            if not slots:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "fail",
                        "message": f"Missing timeslots for: {date_key}"
                    }
                )
            # Validate each timeslot dictionary
            for slot in slots:
                print(slot)
                if "from" not in slot or "to" not in slot:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status": "fail",
                            "message": f"Missing 'from' or 'to' in timeslot for date {date_key}"
                        }
                    )
                try:
                    from_time = datetime.strptime(slot["from"], "%I:%M %p")
                    to_time = datetime.strptime(slot["to"], "%I:%M %p")
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status": "fail",
                            "message": f"Invalid time format in timeslot for date {date_key}. Use HH:MM AM/PM format."
                        }
                    )
                if from_time >= to_time:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status": "fail",
                            "message": f"'from' time must be earlier than 'to' time for date {date_key}"
                        }
                    )
        return v

class AppointmentUpdate(BaseModel):

    date: Optional[List[str]] = None  # Optional date field (e.g., "2024-11-15")
    timeslots: Optional[dict] = None  # List of dictionaries, each with time and label

    class Config:
        orm_mode = True  # Enable ORM mode so that Pydantic will work with SQLAlchemy models
        from_attributes = True

        # Validator to check that each date string is in the correct format
    @field_validator("date")
    def validate_dates(cls, v):
        print(v)
        if v:
            # Ensure each date string is in "YYYY-MM-DD" format
            for date_str in v:
                try:
                    # Attempt to parse each date string using the desired format
                    datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status":"fail",
                            "message":f"Invalid date format {date_str}"
                        }
                    )
        return v