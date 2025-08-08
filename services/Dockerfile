# FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
FROM python:3.11-slim


WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose necessary ports (API, Redis, Frontend)
EXPOSE 8000 6379 8080

CMD ["python3", "main.py"]
