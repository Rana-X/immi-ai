FROM python:3.9-slim

WORKDIR /app

# Copy requirements first
COPY backend/requirements.txt backend/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend code
COPY backend/ backend/

# Expose the port
EXPOSE 8000 