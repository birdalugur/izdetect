FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      build-essential \
      libglib2.0-0 \
      libgl1 \
      libsm6 \
      libxrender1 \
      libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY core ./core
COPY infrastructure ./infrastructure

# Copy API code
COPY api .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
