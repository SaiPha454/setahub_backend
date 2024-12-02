from fastapi import FastAPI, status, Request
import asyncio
from routes.user_route import router as user_router
from routes.user_route import protected_router as protected_user_router
from routes.topic_route import router as topic_router
from routes.appointment_route import router as appointment_router
from routes.booking_route import router as booking_router
from routes.message_route import router as message_router
from database_connection import Base,engine
from models import users_model, message_model, topics_model, booking_model,appointment_model #register table to be created
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from utils.security import SECRET_KEY
import os
from fastapi.staticfiles import StaticFiles
from database_session import SessionLocal


app = FastAPI(title="SETAHub RESTFUL API")

@app.exception_handler(HTTPException)
async def custom_http_exception_handleer(request, exec: HTTPException):
    return JSONResponse(
        status_code= exec.status_code,
        content={
            "error": exec.detail
        }
    )

@app.exception_handler(RequestValidationError)
async def custom_http_exception_handleer(request, exec: RequestValidationError):
    return JSONResponse(
        status_code= status.HTTP_400_BAD_REQUEST,
        content={
            "error": exec.errors()
        }
    )


@app.exception_handler(HTTPException)
async def custom_http_exception_handleer(request: Request, exec: HTTPException):
    return JSONResponse(
        status_code= exec.status_code,
        content=exec.detail
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow all origins
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Background task for periodic check
async def periodic_check():
    while True:
        # Explicitly create a session for the background task
        with SessionLocal() as session:
            try:
                # Call your function to mark overdue bookings
                booking_model.mark_overdated_bookings_as_completed(session=session)
            except Exception as e:
                print(f"Error during periodic check: {e}")
            # Ensure the task runs every 10 seconds
            await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    # Start the background task when the app starts
    asyncio.create_task(periodic_check())  # This runs in the background


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        token = request.cookies.get("jarvis")  # Retrieve token from cookies
        
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                request.state.user_id = payload.get("user_id")
                request.state.email = payload.get("email")
                request.state.role = payload.get("student_id")
                
            except jwt.ExpiredSignatureError:
                return JSONResponse({"detail": "Expire token"}, status_code=401)
            except jwt.InvalidTokenError:
                return JSONResponse({"detail": "Invalid token"}, status_code=401)
        else:
            request.state.user_id = None
            request.state.email = None
            request.state.student_id = None

        return await call_next(request)

app.add_middleware(UserMiddleware)

Base.metadata.create_all(bind=engine)

images_folder_path = os.path.join(os.getcwd(),"images")

app.mount("/images", StaticFiles(directory=images_folder_path), name="images")

app.include_router(user_router)
app.include_router(protected_user_router)
app.include_router(topic_router)
app.include_router(appointment_router)
app.include_router(booking_router)
app.include_router(message_router)


