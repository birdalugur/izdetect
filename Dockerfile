# Use NVIDIA CUDA 12.6 base image with Python support
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
# FROM python:3.11-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY api/ /app/api/
COPY services/ /app/services/
COPY frontend/ /app/frontend/

# Create directory for output data
RUN mkdir -p /app/data

# Expose necessary ports (API, Redis, Frontend)
EXPOSE 8000 6379 8080

# Default command
CMD ["bash", "start.sh"]