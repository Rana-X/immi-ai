FROM python:3.9-slim

WORKDIR /app

# Copy backend requirements first
COPY backend/requirements.txt backend/

# Install dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backend/ backend/

# Set working directory to backend
WORKDIR /app/backend

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 