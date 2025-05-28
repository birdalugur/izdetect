import json
import psutil
import cv2
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from config import Config
from utils import map_labels
from camera_service import CameraService, Camera

import redis
import aioredis

import os
from db import (
    get_active_notifications,
    close_notification,
    clear_all_notifications,
    get_statistics,
    get_notifications_by_date,
    delete_notification,
    delete_all,
)


app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


redis_client = redis.StrictRedis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True
)


# Endpoints
@app.get("/")
async def index():
    return {"message": "Welcome to the Object Detector!"}


@app.get("/notifications")
async def get_notifications():
    notifications = get_active_notifications()

    # `labels` alanini eşle
    notifications = [
        map_labels(notification, Config.LABEL_MAP) for notification in notifications
    ]

    return JSONResponse(notifications)


@app.get("/notifications_by_date")
async def get_notifications_by_date_endpoint(
    start_date: str,
    end_date: str,
    skip: int = 0,
    limit: int = 12,
    labels: str = None,  # Yeni eklenen parametre (örnek: "1,2")
):
    try:
        # Eğer labels parametresi varsa, liste olarak ayarla
        label_list = [int(label) for label in labels.split(",")] if labels else None

        notifications = get_notifications_by_date(
            start_date, end_date, skip, limit, label_list
        )

        # `labels` alanını eşle
        notifications = [
            map_labels(notification, Config.LABEL_MAP) for notification in notifications
        ]

        return JSONResponse(notifications)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/notifications/{notification_id}/close")
async def close_notification_route(
    notification_id: int = Path(..., description="The ID of the notification to close"),
):
    if close_notification(notification_id) == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification closed successfully"}


# TODO: Both delete and options methods are processed.
@app.delete("/delete_notification/{notification_id}")
async def delete_notification_route(notification_id: str):
    """Belirtilen ID'ye sahip bildirimi siler."""
    result = delete_notification(notification_id)
    print("hi")
    if result is not None:
        return {"message": "Bildirim başariyla silindi."}

    raise HTTPException(status_code=404, detail="Bildirim bulunamadi.")


@app.delete("/delete_notifications_by_date")
async def delete_notifications_by_date(start_date: str, end_date: str):
    """Belirtilen tarih araliğindaki tüm bildirimleri siler."""
    try:
        result = delete_all(start_date, end_date)
        return {"message": f"{result.deleted_count} bildirim silindi."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    file_path = os.path.join(Config.OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.post("/start-detection")
async def start_detection():
    try:
        with open("cameras.json", "r") as f:
            cameras = json.load(f)

        rtsp_urls = [cam["ip"] for cam in cameras]

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
        redis = await aioredis.from_url(
            f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}"
        )
        pubsub = redis.pubsub()

        try:
            # Redis kanalini dinlemeye başla
            await pubsub.subscribe(Config.CHANNEL_NAME)

            while True:
                # Eğer istemci bağlantiyi kapattiysa döngüden çik
                if await request.is_disconnected():
                    break

                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1
                )
                if message:
                    message_data = json.loads(message["data"])
                    message_data = map_labels(message_data, Config.LABEL_MAP)
                    yield f"data: {json.dumps(message_data)}\n\n"
                    # yield f"data: {message['data'].decode('utf-8')}\n\n"
        finally:
            # Kaynaklari temizle
            await pubsub.unsubscribe(Config.CHANNEL_NAME)
            await pubsub.close()
            await redis.close()

    # StreamingResponse ile istemciye veri gönder
    return StreamingResponse(redis_event_generator(), media_type="text/event-stream")


@app.get("/video/{camera_id}")
async def video_feed(camera_id: str):
    """Seçilen kameraya göre MJPEG akişi döndür."""

    try:
        cameras = CameraService.read_cameras()

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


@app.post("/set-cameras")
async def set_cameras(cameras: list[Camera]):
    CameraService.write_cameras(cameras)
    return {"message": "Camera information saved successfully"}


@app.get("/get-cameras")
async def get_cameras():
    cameras = CameraService.read_cameras()
    return cameras


@app.get("/ram")
def get_ram_usage():
    ram = psutil.virtual_memory()
    return {"total": ram.total, "used": ram.used}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
