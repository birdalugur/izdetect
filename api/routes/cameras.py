import os

from fastapi import APIRouter, Path, Request
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
from services.camera_service import CameraService, Camera
from services.video_service import VideoService
from services.redis_service import RedisService
from config import Config
from utils.helpers import map_labels
from utils.exceptions import NotFoundException, ServerErrorException

router = APIRouter(prefix="/cameras", tags=["Cameras"])
redis_service = RedisService()


@router.post("/start-detection")
async def start_detection():
    try:
        cameras = CameraService.read_cameras()
        if not cameras:
            raise NotFoundException("No cameras found")
        rtsp_urls = [cam["ip"] for cam in cameras]
        redis_service.delete("camera_urls")
        redis_service.rpush("camera_urls", *rtsp_urls)
        # When starting, set stop_signal to 0
        redis_service.set("stop_signal", "0")
        redis_service.publish("task_control", "start")
        return {
            "message": "Camera URLs set and start command sent",
            "rtsp_urls": rtsp_urls,
        }
    except Exception as e:
        raise ServerErrorException(f"Failed to set camera URLs: {e}")


@router.post("/stop-detection")
async def stop_detection():
    try:
        # First set stop_signal to 1
        redis_service.set("stop_signal", "1")
        redis_service.publish("task_control", "stop")
        return {"message": "Frame producer stopped successfully"}
    except Exception as e:
        raise ServerErrorException(f"Failed to stop frame producer: {e}")


@router.get("/isrunning")
async def is_running():
    try:
        stop_signal = redis_service.get("stop_signal")
        # System is running only if stop_signal is explicitly "0"
        is_running = stop_signal == "0"
        return {"is_running": is_running}
    except Exception as e:
        raise ServerErrorException(f"Failed to check system status: {e}")


# SSE endpoint
@router.get("/events")
async def get_events(request: Request):
    return StreamingResponse(
        redis_service.event_generator(request, Config.CHANNEL_NAME, map_labels),
        media_type="text/event-stream",
    )


@router.get("/video/{camera_id}")
async def video_feed(camera_id: str):
    camera = CameraService.get_camera_by_id(camera_id)
    return StreamingResponse(
        VideoService.generate_frames(camera["ip"], camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/output/{filename}")
async def get_image(
    filename: str = Path(..., description="The name of the file to retrieve"),
):
    file_path = os.path.join(Config.OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        raise NotFoundException("File not found")
    return FileResponse(file_path)


@router.get("/get-cameras")
async def get_cameras():
    return CameraService.read_cameras()


@router.post("/add")
async def add_camera(camera: Camera):
    CameraService.add_camera(camera)
    return {"message": "Kamera başarıyla eklendi"}


@router.delete("/{camera_id}")
async def delete_camera(camera_id: str):
    CameraService.delete_camera(camera_id)
    return {"message": "Kamera başarıyla silindi"}
