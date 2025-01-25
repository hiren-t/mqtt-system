# Use Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install the necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for FastAPI service
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
