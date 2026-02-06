# Dockerfile for MVP Agent v2.0

# Base image (Python 3.10 Slim)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any needed for future)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser
USER appuser
WORKDIR /home/appuser/app

# Copy requirements first (caching layer)
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Add user's bin to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy source code
COPY --chown=appuser:appuser . .

# Expose Gradio port
EXPOSE 7860

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Entrypoint
CMD ["python", "app.py"]
