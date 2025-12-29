# Dockerfile for MVP Agent v2.0

# Base image (Python 3.10 Slim)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any needed for future)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (caching layer)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose Gradio port
EXPOSE 7860

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Entrypoint
CMD ["python", "app.py"]
