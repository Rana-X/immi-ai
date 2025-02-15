FROM python:3.9-slim

# Set working directory to backend directly
WORKDIR /app/backend

# Copy requirements first
COPY backend/requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ .

# Expose the port
EXPOSE 8000

# Command to run the application (using shell form)
CMD uvicorn main:app --host 0.0.0.0 --port $PORT 