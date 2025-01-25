# MQTT System - README

This repository contains a multi-container system with the following components:
1. **Mosquitto Broker:** A lightweight MQTT broker for messaging.
2. **Python MQTT Client:** A client that subscribes to MQTT messages and stores event data in a SQLite database.
3. **REST API Service:** A FastAPI-based service that allows querying device and event data stored by the MQTT client.

This system is built using Docker and Docker Compose for easy deployment and management of multiple services.

## **Table of Contents**
  - System Architecture Overview
  - Setup Instructions
  - API Documentation
  - Test Cases & Example Usage
  - Troubleshooting
##

<details>
<summary> System Architecture Overview </summary>
<br>

The system consists of three services running in separate containers:

1. Mosquitto Broker:
    - An MQTT broker that handles the communication between devices and the MQTT client.
    - Port 1883: MQTT protocol for client communication.
  
2. Python MQTT Client:
   - Subscribes to MQTT topics and processes incoming messages.
   - Stores device and event data in an SQLite database (mqtt_events.db).
   - Uses the gmqtt library for MQTT communication.
   - Validates incoming JSON payloads and logs invalid messages.
  
3. REST API Service (FastAPI):
   - Provides endpoints to interact with the stored data in the SQLite database.
   - Allows retrieving device information and event data via RESTful API calls.
   - Uses FastAPI and Uvicorn to serve the API.
  
All components are orchestrated using Docker Compose to simplify deployment.

</details>

<details>
  <summary> Setup Instructions </summary>
  <br>
  
**Prerequisites**
 - Docker: Install [Docker](https://www.docker.com/)
 - Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/)

## **Step-by-Step Setup**

**1. Clone the repository:**

    git clone https://github.com/hiren-t/mqtt-system.git

Change the current directory to the folder named ```mqtt_system```
        
    cd mqtt_system

**2. **Build and start the services:****
     Docker Compose will automatically build and start the Mosquitto broker, MQTT client, and FastAPI service.

Run the following command in the root directory of the project:

    docker-compose up --build

  **This command will:**
  - Pull the latest Eclipse Mosquitto image.
  - Build the Python MQTT Client and FastAPI REST API services.
  - Start all the services: Mosquitto broker, MQTT client, and FastAPI API.

**3. Verify the services:** 
    After the containers are up, check the logs for each container to verify the services are running:
  - MQTT Broker Logs:
     
        docker logs -f mqtt_broker
     
  - MQTT Client Logs:
     
        docker logs -f mqtt_client
     
   - API Logs:
     
         docker logs -f mqtt_api

**4. Access the REST API:**

- The FastAPI service will be available at http://localhost:8000.
- You can view the API documentation at http://localhost:8000/docs.

**5. Stop the services:** 
  To stop and remove the containers, run:

    docker-compose down

</details>

<details>
<summary> API Documentation </summary>
<br>

The REST API exposes the following endpoints:
## **1. List all registered devices**

**Endpoint:**  ```/devices ```
<br>
**Method:** ``` GET ```
<br>

**Response:**

```json
[
  {
    "device_id": "sensor_001",
    "last_seen": "2025-01-24T10:00:00Z"
  },
  {
    "device_id": "sensor_002",
    "last_seen": "2025-01-24T09:50:00Z"
  }
]
```

**Description:**
This endpoint returns a list of all registered devices along with their last active timestamps.

## **2. Retrieve the last events for a given device**

**Endpoint:** ``` /devices/{device_id}/events ```
<br>
**Method:** ``` GET / ```
<br>
**Query Parameters:**
   ``` api          
    limit (optional): The number of events to retrieve (default is 10).
   ```
**Response:**
```json
[
  {
    "event_id": 1,
    "device_id": "sensor_001",
    "sensor_type": "temperature",
    "sensor_value": 23.5,
    "timestamp": "2025-01-24T10:00:00Z"
  },
  {
    "event_id": 2,
    "device_id": "sensor_001",
    "sensor_type": "humidity",
    "sensor_value": 45.2,
    "timestamp": "2025-01-24T09:55:00Z"
  }
]
```

Description:
This endpoint retrieves the last n events for a given device. The limit can be query parameter to retrieve a specific number of events.

**3. Root Endpoint**

**Endpoint:** ``` / ```
<br>
**Method:** ```GET```
<br>
**Response:**
``` json
{
  "message": "Welcome to the MQTT Event API! Use /docs for API documentation."
}
```
**Description:**
This is the root endpoint that provides a simple welcome message.
</details>

<details>
<summary> Test Cases & Example Usage </summary>
  <br>

  **Test Case 1: Retrieve Devices**
   Make a GET request to ```/devices ```:
                    
    curl http://localhost:8000/devices

Expected Response:
``` json
    [
      {
        "device_id": "sensor_001",
        "last_seen": "2025-01-24T10:00:00Z"
      },
      {
        "device_id": "sensor_002",
        "last_seen": "2025-01-24T09:50:00Z"
      }
    ]
```

  **Test Case 2: Retrieve Events for a Specific Device**

  Make a GET request to ```/devices/{device_id}/events ```: 
      Replace ```{device_id}``` with the actual device ID (e.g., sensor_001).

``` curl
  curl http://localhost:8000/devices/sensor_001/events
```
Expected Response:
``` json
    [
      {
        "event_id": 1,
        "device_id": "sensor_001",
        "sensor_type": "temperature",
        "sensor_value": 23.5,
        "timestamp": "2025-01-24T10:00:00Z"
      },
      {
        "event_id": 2,
        "device_id": "sensor_001",
        "sensor_type": "humidity",
        "sensor_value": 45.2,
        "timestamp": "2025-01-24T09:55:00Z"
      }
    ]
``` 
**Test Case 3: Publish MQTT Message and Store Data**

**1. Publish a message to the MQTT broker (using ```mosquitto_pub``` or another MQTT tool):**
```
    mosquitto_pub -h localhost -p 1883 -t "devices/events" -m '{"device_id": "sensor_001", "sensor_type": "temperature", "sensor_value": 23.5, "timestamp": "2025-01-24T10:00:00Z"}'
```
    
**2.Verify the data is stored:** Make a GET request to ```/devices/sensor_001/events``` to check if the event was stored successfully.
</details>

<details>
<summary> Troubleshooting </summary>
<br>

**1. Container logs:** Check the logs for any issues:
``` docker
docker logs -f mqtt_broker
docker logs -f mqtt_client
docker logs -f mqtt_api
```

**2. SQLite database:** 
If encountered issues with the SQLite database, ensure it is correctly shared between the containers by verifying the volume configuration in ```docker-compose.yml```.

</details>
