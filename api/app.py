import json
import psutil
import cv2
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


import redis
import aioredis

import os
from db import (
    get_active_notifications,
    close_notification,
    clear_all_notifications,
    get_statistics,
)

OUTPUT_FOLDER = os.path.abspath("data/")
CAMERA_URL = "http://10.100.10.94/axis-cgi/mjpg/video.cgi?resolution=1280x800&fps=10"
# RTSP_URL = "rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10"
RTSP_URL = "/home/birdal/izdetect/sahil.mp4"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Redis bağlanti bilgileri
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL_NAME = "event_channel"
redis_client = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
)

selected_label_map = {1: "insan", 2: "arac", 3: "hayvan"}


def map_labels(notification, label_map):
    """Bildirimdeki `labels` alanini eşleyen yardimci fonksiyon."""
    mapped_labels = []
    for label_obj in notification.get("labels", []):
        mapped_label = {label_map.get(int(k), k): v for k, v in label_obj.items()}
        mapped_labels.append(mapped_label)
    notification["labels"] = mapped_labels
    return notification


# Endpoints


@app.get("/")
async def index():
    return {"message": "Welcome to the Object Detector!"}


@app.get("/notifications")
async def get_notifications():
    notifications = get_active_notifications()

    # `labels` alanini eşle
    notifications = [
        map_labels(notification, selected_label_map) for notification in notifications
    ]

    return JSONResponse(notifications)


@app.post("/notifications/{notification_id}/close")
async def close_notification_route(
    notification_id: int = Path(..., description="The ID of the notification to close"),
):
    if close_notification(notification_id) == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification closed successfully"}


@app.get("/statistics")
async def get_statistics_route():
    stats = get_statistics()
    return JSONResponse(content=stats, status_code=200)


@app.post("/notifications/clear-all")
async def clear_all_notifications_route():
    modified_count = clear_all_notifications()
    return {"message": f"{modified_count} bildirim kapatildi"}


@app.get("/output/{filename}")
async def get_image(
    filename: str = Path(..., description="The name of the file to retrieve"),
):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.post("/start-detection")
async def start_detection():
    try:
        with open("cameras.json", "r") as f:
            cameras = json.load(f)

        rtsp_urls = [
            f"rtsp://{cam['username']}:{cam['password']}@{cam['ip']}:{cam['port']}/axis-media/media.amp?adjustablelivestream=1&fps=10"
            for cam in cameras
        ]

        redis_client.delete("camera_urls")
        redis_client.rpush("camera_urls", *rtsp_urls)

        redis_client.publish("task_control", "start")

        return {
            "message": "Camera URLs set and start command sent",
            "rtsp_urls": rtsp_urls,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No cameras found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set camera URLs: {e}")


@app.post("/stop-detection")
async def stop_detection():
    try:
        redis_client.set("stop_signal", "1")
        redis_client.publish("task_control", "stop")
        return {"message": "Frame producer stopped successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to stop frame producer: {e}"
        )


# SSE endpoint
@app.get("/events")
async def get_events(request: Request):
    async def redis_event_generator():
        # Redis bağlantisini aç
        redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
        pubsub = redis.pubsub()

        try:
            # Redis kanalini dinlemeye başla
            await pubsub.subscribe(CHANNEL_NAME)

            while True:
                # Eğer istemci bağlantiyi kapattiysa döngüden çik
                if await request.is_disconnected():
                    break

                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1
                )
                if message:
                    message_data = json.loads(message["data"])
                    message_data = map_labels(message_data, selected_label_map)
                    yield f"data: {json.dumps(message_data)}\n\n"
                    # yield f"data: {message['data'].decode('utf-8')}\n\n"
        finally:
            # Kaynaklari temizle
            await pubsub.unsubscribe(CHANNEL_NAME)
            await pubsub.close()
            await redis.close()

    # StreamingResponse ile istemciye veri gönder
    return StreamingResponse(redis_event_generator(), media_type="text/event-stream")


@app.get("/video/{camera_id}")
async def video_feed(camera_id: str):
    """Seçilen kameraya göre MJPEG akişi döndür."""

    try:
        cameras = read_cameras()

        # Seçilen kameranin bilgilerini al
        selected_camera = next((cam for cam in cameras if cam["id"] == camera_id), None)

        if not selected_camera:
            raise HTTPException(status_code=404, detail="Kamera bulunamadi")

        rtsp_url = selected_camera["ip"]

        def generate_frames(rtsp_url):
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                print(f"{camera_id} için RTSP akişina bağlanilamadi.")
                return

            while True:
                success, frame = cap.read()
                if not success:
                    print(f"{camera_id} için görüntü alinamadi.")
                    break

                _, buffer = cv2.imencode(".jpg", frame)
                frame_bytes = buffer.tobytes()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )

            cap.release()

        return StreamingResponse(
            generate_frames(rtsp_url),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Kamera listesi bulunamadi")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Akiş başlatilamadi: {e}")


class Settings(BaseModel):
    memory: int
    sensitivity: float


@app.post("/update-settings")
async def update_settings(settings: Settings):
    try:
        redis_client.set("tracking:memory", settings.memory)
        redis_client.set("tracking:sensitivity", settings.sensitivity)
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {e}")


class Camera(BaseModel):
    id: str
    ip: str


camera_list = []


@app.post("/set-cameras")
async def set_cameras(cameras: list[Camera]):
    global camera_list
    camera_list = cameras

    with open("cameras.json", "w") as f:
        json.dump([cam.model_dump() for cam in camera_list], f, indent=4)

    return {"message": "Kamera bilgileri kaydedildi!"}


def read_cameras():
    try:
        with open("cameras.json", "r") as f:
            cameras = json.load(f)
        return cameras
    except FileNotFoundError:
        return []


@app.get("/get-cameras")
async def get_cameras():
    global camera_list
    cameras = read_cameras()
    camera_list = cameras
    return cameras


@app.get("/ram")
def get_ram_usage():
    ram = psutil.virtual_memory()
    return {"total": ram.total, "used": ram.used}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
