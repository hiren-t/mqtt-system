# Use Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install the necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the MQTT client script
CMD ["python", "app.py"]
