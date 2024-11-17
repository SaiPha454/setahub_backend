from fastapi import APIRouter, Depends, Body, File, status, UploadFile, Form
from fastapi.responses import JSONResponse
from database_connection import get_db
from sqlalchemy.orm import Session
from schemas.topic_shema import TopicUpdate
from schemas.topic_with_session_schema import TopicReadWithAppointments
from typing import List
from services import topics_service

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=dict)
async def get_all_topics(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10
):
    result = topics_service.get_all_topics_service(db, page, limit)
        # Return a JSONResponse with paginated data
    print("Hello")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status":"success",
            "data": [topic.model_dump() for topic in result],
            "pagination": {
                "page": page,
                "limit": limit,
                "total_results": len(result),  # Or calculate the total count of records from the DB if needed
            }
        }
    )
    
@router.get("/{topic_id}",response_model=TopicReadWithAppointments)
async def get_topic_by_id(
    topic_id: int,
    db: Session=Depends(get_db)
):
    return await topics_service.get_topic_with_appointments(db,topic_id)

# Route for updating a topic
@router.put("/{topic_id}", response_model=dict)
async def update_topic(
    topic_id: int,
    topic_update: TopicUpdate,  # Use Pydantic model for body input
    db: Session = Depends(get_db)
):
    # Pass the updated data from the request body to the service layer

    
    updated_topic = await topics_service.update_topic_service(
        db=db,
        topic_id=topic_id,
        img=topic_update.img,
        topic=topic_update.topic,
        tas=topic_update.tas,
        booked=topic_update.booked
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
        "status": "success",
        "data": {
            "id": updated_topic.id,
            "img": updated_topic.img,
            "topic": updated_topic.topic,
            "tas": updated_topic.tas,
            "booked": updated_topic.booked
            }
        }
    )



# Route for deleting a topic
@router.delete("/{topic_id}", response_model=dict)
async def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db)
):
    await topics_service.delete_topic_service(db, topic_id)
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": f"Topic with id {topic_id} has been deleted."
            }
        )




# Route for creating a new topic
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic: str = Form(...),
    img: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Pass the validated data to the service layer to create a new topic
    created_topic = topics_service.create_topic_service(
        db=db,
        img=img,
        topic=topic,
    )

    # Return a successful response with the created topic data
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    "id": created_topic.id,
                    "img": created_topic.img,
                    "topic": created_topic.topic,
                    "tas": created_topic.tas,
                    "booked": created_topic.booked
                }
            }
        )

    