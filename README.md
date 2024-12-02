# Project Introduction

SETAHub is a platform designed to foster connections and mentorship between senior and junior students within Software Engineering Faculty at KMILT (King Mongkut's Institute of Technology Ladkrabang) . It allows junior students to book time with senior students (Teaching Assistants, or TAs) on various academic topics for guidance and advice. Senior students, on the other hand, can volunteer their time to offer support, helping juniors with their academic questions and challenges.

## Key Features

- **User Authentication:** Secure user registration, login, and session management.
- **User Profile Management:** Allows users to manage their profiles, including updating personal details, changing passwords, and uploading profile pictures.
- **Appointments & Bookings:** Junior students can book appointments with TAs for specific topics, while TAs can manage their availability and upcoming sessions.
- **Topic Management:** Topics can be created, updated, and deleted, allowing TAs and junior students to focus on relevant subjects.
- **Real-Time Messaging:** Facilitates communication between junior and senior students through text and image messages, enabling them to discuss topics, share resources, and offer advice.

## Technologies Used

- **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python.
- **JWT and HTTPOnly:** For secure user authentication and session management.
- **WebSocket:** For real-time messaging between users.
- **PostgreSQL:** Relational database used for storing user and appointment data.
- **SQLAlchemy:** SQL toolkit and Object-Relational Mapping (ORM) library for Python, used to interact with the PostgreSQL database.
- **RESTful API:** Architectural style for developing web services that provide a standard way of communication between the backend and frontend.


## Collaborators
This project is a collaboration between the following individuals:
- Sai Marn Pha (https://github.com/SaiPha454)
- Eaint Kay Khaing Kyaw (https://github.com/daeunek)
- Yanin Saema (https://github.com/NinnY23)

## API Documentation

This documentation provides a brief overview of the endpoints available in the backend service for the SETAHub platform. It outlines the key API endpoints, their purpose, and the corresponding HTTP methods used to interact with the system.


## Endpoints

1. [User Authentication](#authentication)
2. [Users](#users)
3. [Topics](#topics)
4. [Appointments](#appointments)
5. [Bookings](#bookings)
6. [Messaging Websockets](#messaging-websockets)

---

## **User Authentication**

![Screenshot from 2024-12-02 23-42-09](https://github.com/user-attachments/assets/ead5151b-a378-4a3f-8f8d-adda65abcf8c)


### **Register**
**Endpoint:** `/auth/register`  
**Method:** `POST`  

**Description:**  
Registers a new user with the provided username, email, and password.

---

### **Login**

**Endpoint:** `/auth/login`  
**Method:** `POST`  

**Description:**  
Logs in a user with the provided email and password, returning a token for authentication.

---
### **Reset Password**

**Endpoint:** `/auth/reset-password`  
**Method:** `POST`  

**Description:**  
Resets the password for the user by sending a reset link to the provided email.

---
### **Protected Route**

**Endpoint:** `/auth/`  
**Method:** `GET`  

**Description:**  
Accesses a protected route that requires the user to be authenticated for autnetication checking

---


## **Users**

![Screenshot from 2024-12-02 23-44-42](https://github.com/user-attachments/assets/44923d34-c7f8-4b08-aef2-9f0b17c7086d)


### **User Logout**

**Endpoint:** `/users/logout`  
**Method:** `POST`  

**Description:**  
Logs the user out and ends their session.

---

### **Change Password**

**Endpoint:** `/users/change-password`  
**Method:** `PUT`  

**Description:**  
Allows the user to change their password.

---


### **Update Profile Image**

**Endpoint:** `/users/{user_id}/profile`  
**Method:** `PUT`  

**Description:**  
Updates the profile image for the specified user by the given `user_id`.

---

### **Update User Account**

**Endpoint:** `/users/{user_id}`  
**Method:** `PUT`  

**Description:**  
Updates the user account details for the specified user by their `user_id`.

---

### **Get User By ID**

**Endpoint:** `/users/{user_id}`  
**Method:** `GET`  

**Description:**  
Retrieves the user details for the specified user by their `user_id`.

---

### **Get User By ID with Registered Topics**

**Endpoint:** `/users/{user_id}/registered-topics`  
**Method:** `GET`  

**Description:**  
Retrieves the user details along with the topics they are registered for, based on the `user_id`.

---

### **Get User Available Timeslots**

**Endpoint:** `/users/{user_id}/available-timeslots`  
**Method:** `GET`  

**Description:**  
Retrieves the available timeslots for the specified user by their `user_id`, filtered by the `topic_id`.

---

### **Get User Upcoming Booking**

**Endpoint:** `/users/{user_id}/upcoming-bookings`  
**Method:** `GET`  

**Description:**  
Retrieves a list of the upcoming bookings for the specified user by their `user_id`.

---

### **Get User Completed Booking**

**Endpoint:** `/users/{user_id}/completed-bookings`  
**Method:** `GET`  

**Description:**  
Retrieves a list of completed bookings for the specified user by their `user_id`.

---

### **Get User Upcoming TA Appointments**

**Endpoint:** `/users/{user_id}/upcoming-appointments`  
**Method:** `GET`  

**Description:**  
Retrieves the upcoming TA appointments for the specified user by their `user_id`.

---

### **Get User Completed TA Appointment**

**Endpoint:** `/users/{user_id}/completed-appointments`  
**Method:** `GET`  

**Description:**  
Retrieves the completed TA appointments for the specified user by their `user_id`.

---

## **Topics**

![Screenshot from 2024-12-03 00-19-51](https://github.com/user-attachments/assets/64cb44d0-58c2-4dba-a992-efda84e00897)


### **Get All Topics**

**Endpoint:** `/topics/`  
**Method:** `GET`  

**Description:**  
Retrieves all the topics with optional pagination via `page` and `limit` query parameters.

---

### **Create Topic**

**Endpoint:** `/topics/`  
**Method:** `POST`  

**Description:**  
Creates a new topic. The request body should contain the data for the topic in `multipart/form-data` format.

---

### **Get Topic By Id**

**Endpoint:** `/topics/{topic_id}`  
**Method:** `GET`  

**Description:**  
Retrieves the topic by the specified `topic_id`.

---

### **Update Topic**

**Endpoint:** `/topics/{topic_id}`  
**Method:** `PUT`  

**Description:**  
Updates the topic specified by `topic_id`. The request body should contain the data to update the topic in `application/json` format.

---

### **Delete Topic**

**Endpoint:** `/topics/{topic_id}`  
**Method:** `DELETE`  

**Description:**  
Deletes the topic specified by `topic_id`.

---


## **Appointments**

![Screenshot from 2024-12-03 00-22-47](https://github.com/user-attachments/assets/9833ec4c-5a66-4742-97ec-b8bfb0074156)


### **Create Appointment**

**Endpoint:** `/appointments/`  
**Method:** `POST`  

**Description:**  
Creates a new appointment. The request body should contain the appointment data in `application/json` format.

---

### **Get Ta Session By Id**

**Endpoint:** `/appointments/{appointment_id}`  
**Method:** `GET`  

**Description:**  
Retrieves the TA session by the specified `appointment_id`.

---

### **Update Ta Session**

**Endpoint:** `/appointments/{appointment_id}`  
**Method:** `PUT`  

**Description:**  
Updates the TA session specified by `appointment_id`. The request body should contain the data to update the session in `application/json` format.

---

### **Delete Ta Session**

**Endpoint:** `/appointments/{appointment_id}`  
**Method:** `DELETE`  

**Description:**  
Deletes the TA session specified by `appointment_id`.

---

## **Bookings**


![Screenshot from 2024-12-03 00-24-41](https://github.com/user-attachments/assets/bcb9503d-f722-4803-994d-085bdd82fcd2)


### **Create Booking**

**Endpoint:** `/bookings/`  
**Method:** `POST`  

**Description:**  
Creates a new booking. The request body should contain the booking data in `application/json` format.

---

### **Get Booking By Id**

**Endpoint:** `/bookings/{booking_id}`  
**Method:** `GET`  

**Description:**  
Retrieves the booking by the specified `booking_id`.

---

### **Complete Booking**

**Endpoint:** `/bookings/{booking_id}`  
**Method:** `PUT`  

**Description:**  
Marks the booking specified by `booking_id` as complete.

---

### **Delete Booking By Id**

**Endpoint:** `/bookings/{booking_id}`  
**Method:** `DELETE`  

**Description:**  
Deletes the booking specified by `booking_id`.

---

## **Messaging Websockets**




![Screenshot from 2024-12-03 00-27-41](https://github.com/user-attachments/assets/78cdad2a-39b9-4b5e-bdcc-5eb74af1ea73)


### **Send Message**

**Endpoint:** `/messages/{from_user_id}/to/{to_user_id}`  
**Method:** `POST`  

**Description:**  
Sends a message from the user with `from_user_id` to the user with `to_user_id`. The request body should contain the message data in `application/json` format.

---

### **Send Image Message**

**Endpoint:** `/messages/{from_user_id}/to/{to_user_id}/images`  
**Method:** `POST`  

**Description:**  
Sends an image message from the user with `from_user_id` to the user with `to_user_id`. The request body should be in `multipart/form-data` format, containing the image data.

---

### **Get Unread Messages**

**Endpoint:** `/messages/{user_id}/unread`  
**Method:** `GET`  

**Description:**  
Retrieves all unread messages for the user with `user_id`.

---

### **Get Messages Between Users**

**Endpoint:** `/messages/{from_user_id}/with/{to_user_id}`  
**Method:** `GET`  

**Description:**  
Retrieves all messages exchanged between the user with `from_user_id` and the user with `to_user_id`.

---
## License

This project is licensed under the MIT License.

