# app/services/camera_service.py
import json
from typing import List
from pydantic import BaseModel
from fastapi import HTTPException

class Camera(BaseModel):
    id: str
    ip: str

class CameraService:
    CAMERA_FILE = "cameras.json"

    @staticmethod
    def read_cameras() -> List[dict]:
        try:
            with open(CameraService.CAMERA_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    @staticmethod
    def write_cameras(cameras: List[Camera]):
        with open(CameraService.CAMERA_FILE, "w") as f:
            json.dump([cam.model_dump() for cam in cameras], f, indent=4)

    @staticmethod
    def get_camera_by_id(camera_id: str) -> dict:
        cameras = CameraService.read_cameras()
        camera = next((cam for cam in cameras if cam["id"] == camera_id), None)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        return camera