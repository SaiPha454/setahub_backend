from fastapi import HTTPException, status, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.topics_model import Topic
from models import topics_model
from schemas.topic_shema import TopicRead
from models.topics_model import get_all_topics, update_topic, delete_topic, get_topic_by_topic
from typing import Optional
from pathlib import Path
import uuid
import shutil
from typing import List

from schemas.topic_with_session_schema import AppointmentTopicRead, TopicReadWithAppointments

# Define directory to store uploaded images
IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)  # Create the directory if it doesn't exist


# Service layer method to handle pagination and return response
def get_all_topics_service(db: Session, page: int = 1, limit: int = 10)-> List[Topic] :
    # Fetch paginated topics from the database
    offset = (page - 1) * limit  # Calculate the offset for pagination
    topics = get_all_topics(db, offset, limit)

    # Convert to a list of Pydantic models for serialization
    result = [TopicRead.model_validate(topic) for topic in topics]

    return result


async def get_topic_with_appointments(db: Session, topic_id: int):

    topic = await topics_model.get_topic_with_sessions(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail={
            "status":"fail",
            "message":"Topic not found"
        })
    print("About to fetch ....", topic)
    topic_with_appointments = TopicReadWithAppointments(
        id=topic.id,
        topic=topic.topic,
        img=topic.img,
        tas=topic.tas,
        booked=topic.booked,
        appointments=[
            AppointmentTopicRead(
                id=apppointment.id,
                topic_id=apppointment.topic_id,
                ta_id=apppointment.ta_id,
                date=apppointment.date,  # Ensure date is a string
                timeslots=apppointment.timeslots,
                ta=apppointment.ta,
                topic=topic
            ) for apppointment in topic.appointments
        ]
    )
    print("Fetched ....")
    return topic_with_appointments

# Update a topic by ID
async def update_topic_service(db: Session, topic_id: int, img: Optional[str] = None, topic: Optional[str] = None, 
                         tas: Optional[int] = None, booked: Optional[int] = None) -> Topic:
    updated_topic = await update_topic(db, topic_id, img, topic, tas, booked)
    if not updated_topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "status":"fail",
            "message": "Topic not found"
            }
        )

    return updated_topic



# Delete a topic by ID
async def delete_topic_service(db: Session, topic_id: int) -> bool:
    success = delete_topic(db, topic_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
            "status":"fail",
            "message":"Topic not found"
        })
    return True

def create_topic_service(db: Session, topic: str, img: UploadFile = None) -> Topic:

    if img: 
        if img.content_type not in ["image/jpeg", "image/png", "image/gif"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status":"fail",
                    "message":"Only image files are allowed (jpeg, png, gif)."
                }
            )
    # Check if a topic with the same name already exists (optional, can be removed based on requirements)
    existing_topic = get_topic_by_topic(db, topic)
    if existing_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status":"fail",
                "message":"Topic with this name already exists."
            }
        )

    # Create a new topic instance
    try:
        img_url = "/images/default.png"
        if img:
            # Generate a unique filename for the image
            unique_filename = f"{uuid.uuid4()}_{img.filename}"
            img_path = IMAGE_DIR / unique_filename

            # Save the uploaded file with the unique filename
            with img_path.open("wb") as buffer:
                shutil.copyfileobj(img.file, buffer)

            # Create the URL for the saved image
            img_url = f"/images/{unique_filename}"

        # Create the topic record in the database
        new_topic = Topic(img=img_url, topic=topic, tas=0, booked=0)
        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)
        
        return new_topic

    except Exception as e:
        # Rollback in case of any error and raise an HTTPException
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status":"fail",
                "message":"An error occurred while creating the topic"
            }
        )
    
