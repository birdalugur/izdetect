# IzDetect - Real-Time Object Detection System

IzDetect is a comprehensive, full-stack object detection and tracking system designed to monitor multiple camera streams in real-time. By leveraging state-of-the-art deep learning models, it identifies and tracks objects (such as people, vehicles, and animals), generating real-time notifications and keeping a detailed history of detection sessions.

---

## 🏗️ System Architecture

The application is built using a modern, microservices-oriented architecture, consisting of the following core components:

### 1. API Service (`/api`)
The central control plane of the system, built with **Python 3.11** and **FastAPI**.
- Manages camera configurations, system settings, and detection sessions.
- Uses **MongoDB** for persistent storage of configurations and historical data.
- Uses **Redis** for pub/sub messaging, state management, and task control.
- Pushes real-time detection events to the frontend via **Server-Sent Events (SSE)**.

### 2. Inference Workers (`/workers`)
The GPU-accelerated engine responsible for analyzing video streams.
- Built with **PyTorch** and utilizes the **DETR (DEtection TRansformer)** model for high-accuracy object detection.
- Employs the **SORT (Simple Online and Realtime Tracking)** algorithm to track objects seamlessly across video frames.
- Processes individual RTSP camera streams using a robust pipeline: `FrameProducer -> Inference -> DetectionProcessor -> NotifyProcessor`.
- Publishes detection events to Redis and records detection sessions in MongoDB.

### 3. Frontend Web Interface (`/frontend`)
A responsive, real-time user interface designed to give operators full control and visibility.
- Built with **Svelte** and styled with **Tailwind CSS**.
- Connects to the API to display an interactive dashboard.
- Displays live camera feeds, active detection sessions, and pops up real-time notifications as objects are detected.

---

## 🚀 Technology Stack

- **Backend / API**: Python 3.11, FastAPI, Uvicorn, SSE
- **Machine Learning / AI**: PyTorch, Transformers (DETR), OpenCV, PyTorch CUDA
- **Algorithm**: SORT (Kalman Filter-based object tracking)
- **Frontend**: Node 21, Svelte, Tailwind CSS, Rollup
- **Database / Cache**: MongoDB, Redis
- **DevOps**: Docker, Docker Compose

---

## 📂 Directory Structure

```text
izdetect/
├── api/                  # FastAPI backend server
│   ├── routes/           # REST endpoints (cameras, notifications, system)
│   ├── services/         # Business logic (camera service, redis pub/sub)
│   └── ...
├── workers/              # Deep Learning Inference and processing pipeline
│   ├── core/             # MongoDB/Redis clients, SORT tracking, utils
│   ├── processors/       # Inference pipeline components
│   └── ...
├── frontend/             # Svelte web application
│   ├── src/              # Svelte components and logic
│   └── package.json      
├── data/                 # Volume mounts for MongoDB, Redis, and app data
└── docker-compose.yml    # Main stack configuration file
```

---

## 🛠️ Getting Started

The easiest way to run the entire IzDetect system is by using Docker Compose. Ensure you have Docker and Docker Compose installed, along with NVIDIA Container Toolkit for GPU acceleration.

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU with appropriate drivers
- NVIDIA Container Toolkit (to enable `--gpus all` in Docker)

### Running the System

1. **Clone the repository** (if you haven't already) and navigate to the project root:
   ```bash
   cd /path/to/izdetect
   ```

2. **Start the stack** using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```

This command will initialize and start the following services:
- **Redis** (`redis`): on port `6379`
- **MongoDB** (`mongodb`): on port `27017`
- **API** (`api`): on port `8000` (`http://localhost:8000`)
- **Frontend** (`frontend`): on port `3000` (`http://localhost:3000`)
- **Workers** (`workers`): Runs in the background (requires GPU)

### Accessing the System
- **Web Interface**: Open your browser and navigate to `http://localhost:3000`
- **API Swagger CLI**: Detailed API documentation is available at `http://localhost:8000/docs`

---

## 🔧 Workflow & Process

1. **Add a Camera**: An RTSP stream URL is added via the frontend dashboard. The API saves this to MongoDB and Redis.
2. **Start Detection**: The user starts a detection session. The API sends a `start` control signal to the `task_control` Redis channel.
3. **Inference**: The Worker picks up the signal, connects to the RTSP stream, and begins processing frames through the DETR model.
4. **Tracking**: Evaluated frames are passed through the SORT tracker to maintain object IDs.
5. **Notification**: When an object (e.g., a person or vehicle) is confidently detected and tracked, the Worker publishes an event to the `event_channel` in Redis.
6. **Real-time Alert**: The API consumes the event from Redis and broadcasts it via SSE to the Frontend, alerting the user instantly.

---

## ⚠️ Known Limitations & Scope

- **GPU Requirement**: The inference worker heavily relies on PyTorch and CUDA; running on CPU only will result in severely degraded frame rates and high latency.
- **Authentication**: User authentication and authorization are currently not implemented out-of-the-box. The system is designed to run in a secure, internal network.
- **Scaling limitations**: The current worker pipeline architecture is robust but relies heavily on 1-to-1 processing queues. Horizontal scaling of the worker node would require distributed queue management.
