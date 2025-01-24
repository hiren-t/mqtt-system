import asyncio
import json
import logging
import sqlite3
from gmqtt import Client as MQTTClient
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants from environment variables
BROKER_HOST = os.getenv('BROKER_HOST', 'broker.emqx.io')  # Default to mqtt.example.com if not set
BROKER_PORT = int(os.getenv('BROKER_PORT', 1883))  # Default to 1883 if not set
TOPIC = '/devices/events'  # Subscription topic
CLIENT_ID = 'mqtt_client_1'  # Unique Client ID for the connection

# Optional: Authentication details from environment variables
USERNAME = os.getenv('USERNAME', 'your_username')
PASSWORD = os.getenv('PASSWORD', 'your_password')

# Logging configuration
logging.basicConfig(
    filename='invalid_messages.log',
    level=logging.ERROR,
    format='%(asctime)s - %(message)s'
)

# JSON schema for validation
MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "device_id": {"type": "string"},
        "sensor_type": {"type": "string"},
        "sensor_value": {"type": "number"},
        "timestamp": {"type": "string", "format": "date-time"}
    },
    "required": ["device_id", "sensor_type", "sensor_value", "timestamp"],
    "additionalProperties": False
}

# SQLite database setup
DB_NAME = os.getenv('DB_NAME', 'mqtt_events.db')  # Default to mqtt_events.db if not set


def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Devices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Devices (
        device_id TEXT PRIMARY KEY,
        last_seen TEXT
    )
    """)

    # Create Events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        sensor_type TEXT,
        sensor_value REAL,
        timestamp TEXT,
        FOREIGN KEY (device_id) REFERENCES Devices(device_id)
    )
    """)

    # Indexing for efficient querying
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_id ON Events(device_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON Events(timestamp)")

    conn.commit()
    conn.close()

def store_message_in_database(message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    device_id = message["device_id"]
    sensor_type = message["sensor_type"]
    sensor_value = message["sensor_value"]
    timestamp = message["timestamp"]

    # Update or insert into Devices table
    cursor.execute("""
    INSERT INTO Devices (device_id, last_seen)
    VALUES (?, ?)
    ON CONFLICT(device_id) DO UPDATE SET last_seen=excluded.last_seen
    """, (device_id, timestamp))

    # Insert into Events table
    cursor.execute("""
    INSERT INTO Events (device_id, sensor_type, sensor_value, timestamp)
    VALUES (?, ?, ?, ?)
    """, (device_id, sensor_type, sensor_value, timestamp))

    conn.commit()
    conn.close()

# Callback when the client connects to the broker
def on_connect(client, flags, rc, properties):
    print("Connected to MQTT broker!")
    client.subscribe(TOPIC)  # Subscribe to the /devices/events topic

# Callback to process and validate JSON messages
def on_message(client, topic, payload, qos, properties):
    try:
        # Decode and parse JSON payload
        message = json.loads(payload.decode())
        
        # Validate message against schema
        validate(instance=message, schema=MESSAGE_SCHEMA)

        # Store valid message in the database
        store_message_in_database(message)
        print(f"Stored valid message: {message}")

    except ValidationError as ve:
        error_message = f"Validation error: {ve.message}. Payload: {payload.decode()}"
        print(error_message)
        logging.error(error_message)

    except json.JSONDecodeError:
        error_message = f"JSON decode error. Payload: {payload.decode()}"
        print(error_message)
        logging.error(error_message)

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}. Payload: {payload.decode()}"
        print(error_message)
        logging.error(error_message)

# Callback when the client disconnects
def on_disconnect(client, packet, exc=None):
    print("Disconnected from MQTT broker")

# Callback when the client subscribes to a topic
def on_subscribe(client, mid, qos, properties):
    print(f"Subscribed to topic '{TOPIC}' with MID {mid}")

# Main async function
async def main():
    # Setup database
    setup_database()

    # MQTT client setup
    client = MQTTClient(CLIENT_ID)
    client.set_auth_credentials(USERNAME, PASSWORD)  # Set authentication
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    # Connect to the broker
    await client.connect(BROKER_HOST, BROKER_PORT)

    # Keep the client running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Disconnecting...")
        await client.disconnect()

# Run the client
if __name__ == '__main__':
    asyncio.run(main())