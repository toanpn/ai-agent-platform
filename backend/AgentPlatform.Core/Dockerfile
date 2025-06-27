# Use Python 3.11 slim image for smaller footprint
FROM docker.io/library/python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8000

# Install system dependencies for potential native package compilation
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create uploads directory if it doesn't exist
RUN mkdir -p uploads

# Expose the port the app runs on (configurable via PORT env var, default 8000 for Docker)
EXPOSE 8000

# Run the API server
CMD ["python", "start_api.py"]
