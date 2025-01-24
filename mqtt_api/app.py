from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

# FastAPI app instance
app = FastAPI(title="MQTT Event API", version="1.0")

# Database file
DB_NAME = "mqtt_events.db"

# Helper function to connect to the database
def get_db_connection():
    return sqlite3.connect(DB_NAME)

# Data models
class Device(BaseModel):
    device_id: str
    last_seen: str

class Event(BaseModel):
    event_id: int
    device_id: str
    sensor_type: str
    sensor_value: float
    timestamp: str

# Routes
@app.get("/devices", response_model=List[Device])
def list_devices():
    """
    Retrieve all registered devices with their last active timestamps.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT device_id, last_seen FROM Devices ORDER BY last_seen DESC")
        devices = cursor.fetchall()
        conn.close()

        return [{"device_id": device[0], "last_seen": device[1]} for device in devices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/devices/{device_id}/events", response_model=List[Event])
def get_device_events(device_id: str, limit: Optional[int] = 10):
    """
    Retrieve the last events for a given device.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT event_id, device_id, sensor_type, sensor_value, timestamp 
        FROM Events 
        WHERE device_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
        """, (device_id, limit))
        events = cursor.fetchall()
        conn.close()

        if not events:
            raise HTTPException(status_code=404, detail=f"No events found for device '{device_id}'.")

        return [{"event_id": event[0], "device_id": event[1], "sensor_type": event[2],
                 "sensor_value": event[3], "timestamp": event[4]} for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the MQTT Event API! Use /docs for API documentation."}
