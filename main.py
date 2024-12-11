from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import pymysql
from datetime import datetime

app = FastAPI()

# Database credentials
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "room_scheduler_db"

# Function to connect to MySQL server (without a specific database)
def dbconnect_to_server():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL server: {e}")
        return None

# Function to connect to the specific database
def dbconnect():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# Function to create the database if it doesn't exist
def create_database():
    connection = dbconnect_to_server()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
            connection.commit()
        connection.close()

# Function to create the necessary tables for the application
def create_tables():
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            # Create 'rooms' table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    location VARCHAR(255),
                    capacity INT
                );
            """)

            # Create 'users' table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255)
                );
            """)

            # Create 'appointments' table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    room_id INT,
                    start_time DATETIME,
                    end_time DATETIME,
                    purpose VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'scheduled',
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                );
            """)
            connection.commit()
        connection.close()

# Run this code when the application starts
@app.on_event("startup")
async def startup_event():
    create_database()  # Automatically create the database if not exists
    create_tables()    # Automatically create the necessary tables

# Models
class User(BaseModel):
    name: str
    email: str

class Room(BaseModel):
    name: str
    capacity: int
    location: str

class Appointment(BaseModel):
    user_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    purpose: str

# USER FUNCTIONS
@app.post("/users")
def create_user(user: User):
    try:
        connection = dbconnect()
        if not connection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
            cursor.execute(sql, (user.name, user.email))
            connection.commit()
        connection.close()
        return {"message": "User created successfully"}
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/users")
def get_all_users():
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
        connection.close()
        return users

@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        connection.close()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET name = %s, email = %s WHERE id = %s"
            cursor.execute(sql, (user.name, user.email, user_id))
            connection.commit()
        connection.close()
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
        connection.close()
    return {"message": "User deleted successfully"}

# ROOM FUNCTIONS
@app.post("/rooms")
def create_room(room: Room):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            sql = "INSERT INTO rooms (name, location, capacity) VALUES (%s, %s, %s)"
            cursor.execute(sql, (room.name, room.location, room.capacity))
            connection.commit()
        connection.close()
    return {"message": "Room created successfully"}

@app.get("/rooms")
def get_all_rooms():
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM rooms")
            rooms = cursor.fetchall()
        connection.close()
        return rooms

@app.get("/rooms/{room_id}")
def get_room_by_id(room_id: int):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
            room = cursor.fetchone()
        connection.close()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room

@app.put("/rooms/{room_id}")
def update_room(room_id: int, room: Room):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            sql = "UPDATE rooms SET name = %s, location = %s, capacity = %s WHERE id = %s"
            cursor.execute(sql, (room.name, room.location, room.capacity, room_id))
            connection.commit()
        connection.close()
    return {"message": "Room updated successfully"}

@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
            connection.commit()
        connection.close()
    return {"message": "Room deleted successfully"}

# APPOINTMENT FUNCTIONS
@app.post("/appointments")
def create_appointment(appointment: Appointment):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO appointments (user_id, room_id, start_time, end_time, purpose) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (appointment.user_id, appointment.room_id, appointment.start_time, appointment.end_time, appointment.purpose))
            connection.commit()
        connection.close()
    return {"message": "Appointment created successfully"}

@app.get("/appointments")
def get_all_appointments():
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM appointments")
            appointments = cursor.fetchall()
        connection.close()
        return appointments

@app.get("/appointments/{appointment_id}")
def get_appointment_by_id(appointment_id: int):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
            appointment = cursor.fetchone()
        connection.close()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment

@app.put("/appointments/{appointment_id}")
def update_appointment(appointment_id: int, appointment: Appointment):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            sql = """
                UPDATE appointments 
                SET user_id = %s, room_id = %s, start_time = %s, end_time = %s, purpose = %s 
                WHERE id = %s
            """
            cursor.execute(sql, (appointment.user_id, appointment.room_id, appointment.start_time, appointment.end_time, appointment.purpose, appointment_id))
            connection.commit()
        connection.close()
    return {"message": "Appointment updated successfully"}

@app.delete("/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int):
    connection = dbconnect()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
            connection.commit()
        connection.close()
    return {"message": "Appointment cancelled"}
