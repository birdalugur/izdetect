import asyncio
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
RTSP_URL = "rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10"

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


# Endpoints


@app.get("/")
async def index():
    return {"message": "Welcome to the Object Detector!"}


@app.get("/notifications")
async def get_notifications():
    notifications = get_active_notifications()

    # `labels` alanini eşle
    for notification in notifications:
        mapped_labels = []
        for label_obj in notification.get("labels", []):
            mapped_label = {
                selected_label_map.get(int(k), k): v for k, v in label_obj.items()
            }
            mapped_labels.append(mapped_label)
        notification["labels"] = mapped_labels

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
        redis_client.set("camera_url", RTSP_URL)
        return {
            "message": "Camera URL set successfully",
            "camera_url": RTSP_URL,
            "default_camera_url": CAMERA_URL,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set camera URL: {e}")


@app.post("/stop-detection")
async def stop_detection():
    try:
        redis_client.set("stop_signal", "1")
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

                # Redis kanalindan mesaj al
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1
                )
                if message:
                    yield f"data: {message['data'].decode('utf-8')}\n\n"
        finally:
            # Kaynaklari temizle
            await pubsub.unsubscribe(CHANNEL_NAME)
            await pubsub.close()
            await redis.close()

    # StreamingResponse ile istemciye veri gönder
    return StreamingResponse(redis_event_generator(), media_type="text/event-stream")


def generate_frames():
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print("RTSP akişina bağlanilamadi.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("Görüntü alinamadi.")
            break

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

    cap.release()


@app.get("/video")
async def video_feed():
    """Tarayiciya MJPEG akişi döndür."""
    return StreamingResponse(
        generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
