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


@router.post("/start-detection", summary="Nesne tespiti başlat")
async def start_detection():
    """
    Tüm kayıtlı kameralar için RTSP bağlantılarını Redis'e kaydeder, 
    tespit sürecini başlatmak için ilgili sinyali yayınlar.

    Returns:
        dict: Başlatma mesajı ve RTSP URL listesi.
    """
    try:
        cameras = CameraService.read_cameras()
        if not cameras:
            raise NotFoundException("No cameras found")
        rtsp_urls = [cam["ip"] for cam in cameras]
        redis_service.delete("camera_urls")
        redis_service.rpush("camera_urls", *rtsp_urls)
        redis_service.set("stop_signal", "0")
        redis_service.publish("task_control", "start")
        return {
            "message": "Camera URLs set and start command sent",
            "rtsp_urls": rtsp_urls,
        }
    except Exception as e:
        raise ServerErrorException(f"Failed to set camera URLs: {e}")


@router.post("/stop-detection", summary="Nesne tespitini durdur")
async def stop_detection():
    """
    Tespit sürecini durdurmak için Redis'e dur sinyali gönderir.

    Returns:
        dict: Durdurma işlemi başarılı mesajı.
    """
    try:
        redis_service.set("stop_signal", "1")
        redis_service.publish("task_control", "stop")
        return {"message": "Frame producer stopped successfully"}
    except Exception as e:
        raise ServerErrorException(f"Failed to stop frame producer: {e}")


@router.get("/isrunning", summary="Sistem çalışıyor mu kontrol et")
async def is_running():
    """
    Redis'ten 'stop_signal' bilgisini kontrol ederek sistemin çalışıp çalışmadığını döner.

    Returns:
        dict: `is_running` anahtarıyla boolean değer.
    """
    try:
        stop_signal = redis_service.get("stop_signal")
        is_running = stop_signal == "0"
        return {"is_running": is_running}
    except Exception as e:
        raise ServerErrorException(f"Failed to check system status: {e}")


@router.get("/events", summary="Gerçek zamanlı olay akışı (SSE)")
async def get_events(request: Request):
    """
    Sunucu-taraflı olay (Server-Sent Events) akışı sağlar.

    Args:
        request (Request): Client bağlantı isteği.

    Returns:
        StreamingResponse: Canlı olay akışı.
    """
    return StreamingResponse(
        redis_service.event_generator(request, Config.CHANNEL_NAME, map_labels),
        media_type="text/event-stream",
    )


@router.get("/video/{camera_id}", summary="Kamera canlı video akışı")
async def video_feed(camera_id: str):
    """
    Belirtilen kamera için canlı video akışı sağlar.

    Args:
        camera_id (str): Kamera kimliği.

    Returns:
        StreamingResponse: MJPEG formatında video akışı.
    """
    camera = CameraService.get_camera_by_id(camera_id)
    return StreamingResponse(
        VideoService.generate_frames(camera["ip"], camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/output/{filename}", summary="Çıktı görselini getir")
async def get_image(
    filename: str = Path(..., description="İndirilecek dosya adı"),
):
    """
    Belirtilen çıktı klasöründen dosya getirir.

    Args:
        filename (str): Dosya adı.

    Returns:
        FileResponse: Görsel dosyası.
    """
    file_path = os.path.join(Config.OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        raise NotFoundException("File not found")
    return FileResponse(file_path)


@router.get("/get-cameras", summary="Kayıtlı kameraları getir")
async def get_cameras():
    """
    Tüm kayıtlı kameraları döner.

    Returns:
        List[dict]: Kamera bilgileri listesi.
    """
    return CameraService.read_cameras()


@router.post("/add", summary="Yeni kamera ekle")
async def add_camera(camera: Camera):
    """
    Yeni bir kamera kaydı oluşturur.

    Args:
        camera (Camera): Eklenecek kamera bilgileri.

    Returns:
        dict: Başarı mesajı.
    """
    CameraService.add_camera(camera)
    return {"message": "Kamera başarıyla eklendi"}


@router.delete("/{camera_id}", summary="Kamera sil")
async def delete_camera(camera_id: str):
    """
    Belirtilen ID'ye sahip kamerayı siler.

    Args:
        camera_id (str): Silinecek kamera kimliği.

    Returns:
        dict: Başarı mesajı.
    """
    CameraService.delete_camera(camera_id)
    return {"message": "Kamera başarıyla silindi"}
