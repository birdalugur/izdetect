from typing import List
from pydantic import BaseModel
from fastapi import HTTPException
import db_client


class Camera(BaseModel):
    id: str
    ip: str


class CameraService:
    @staticmethod
    def read_cameras() -> List[dict]:
        return db_client.get_cameras()

    @staticmethod
    def get_camera_by_id(camera_id: str) -> dict:
        cameras = CameraService.read_cameras()
        camera = next((cam for cam in cameras if cam["id"] == camera_id), None)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        return camera

    @staticmethod
    def add_camera(camera: Camera):
        try:
            db_client.add_camera(camera.model_dump())
        except Exception:
            # Assuming db_client raises HTTPError if fails (400)
            raise HTTPException(status_code=400, detail="Camera ID already exists or database error")

    @staticmethod
    def delete_camera(camera_id: str):
        try:
            db_client.delete_camera(camera_id)
        except Exception:
            # Assuming db_client raises HTTPError if fails (404)
            raise HTTPException(status_code=404, detail="Camera not found")
