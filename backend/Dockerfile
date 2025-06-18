FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=llm_websocket_api.settings

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create static directory
RUN mkdir -p /app/staticfiles

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "llm_websocket_api.asgi:application"] 