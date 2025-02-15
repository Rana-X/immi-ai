FROM python:3.9-slim

# Install bash
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/backend

# Copy requirements first
COPY backend/requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ ./

# Make the startup script executable
RUN chmod +x start.sh

# Expose the port
EXPOSE 8000

# Run the application with shell form to handle environment variables
CMD /usr/local/bin/uvicorn main:app --host 0.0.0.0 --port $PORT 