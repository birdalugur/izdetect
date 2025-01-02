import os
from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from db import (
    get_active_notifications,
    close_notification,
    clear_all_notifications,
    get_statistics,
)


OUTPUT_FOLDER = os.path.abspath("../od-data/")
CAMERA_URL = "http://10.100.10.94/axis-cgi/mjpg/video.cgi?resolution=1280x800&fps=10"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


async def index(request):
    return JSONResponse({"message": "Welcome to the Object Detector!"})


async def get_notifications(request):
    notifications = get_active_notifications()
    return JSONResponse(notifications, status_code=200)


async def close_notification_route(request):
    notification_id = request.path_params["notification_id"]
    if close_notification(notification_id) == 0:
        return JSONResponse({"error": "Notification not found"}, status_code=404)
    return JSONResponse(
        {"message": "Notification closed successfully"}, status_code=200
    )


async def get_statistics_route(request):
    stats = get_statistics()
    return JSONResponse(stats, status_code=200)


async def clear_all_notifications_route(request):
    modified_count = clear_all_notifications()
    return JSONResponse(
        {"message": f"{modified_count} bildirim kapatildi"}, status_code=200
    )


async def get_image(request):
    filename = request.path_params["filename"]
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    return FileResponse(file_path)


async def send_camera_url(request):
    camera_url = (
        CAMERA_URL
    )
    return JSONResponse({"url": camera_url})


routes = [
    Route("/", endpoint=index),
    Route("/notifications", endpoint=get_notifications),
    Route(
        "/notifications/{notification_id}/close",
        endpoint=close_notification_route,
        methods=["POST"],
    ),
    Route("/statistics", endpoint=get_statistics_route),
    Route(
        "/notifications/clear-all",
        endpoint=clear_all_notifications_route,
        methods=["POST"],
    ),
    Route("/output/{filename}", endpoint=get_image),
    Route("/camurl", endpoint=send_camera_url),
]

app = Starlette(debug=True, routes=routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
