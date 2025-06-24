# app/services/camera_service.py
import json
from typing import List
from pydantic import BaseModel
from fastapi import HTTPException
from db import db


class Camera(BaseModel):
    id: str
    ip: str


camera_collection = db["cameras"]


class CameraService:
    CAMERA_FILE = "cameras.json"

    @staticmethod
    def read_cameras() -> List[dict]:
        cameras = list(camera_collection.find())
        return [{"id": cam["id"], "ip": cam["ip"]} for cam in cameras]

    @staticmethod
    def get_camera_by_id(camera_id: str) -> dict:
        cameras = CameraService.read_cameras()
        camera = next((cam for cam in cameras if cam["id"] == camera_id), None)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        return camera

    @staticmethod
    def add_camera(camera: Camera):
        if camera_collection.find_one({"id": camera.id}):
            raise HTTPException(status_code=400, detail="Camera ID already exists")
        camera_collection.insert_one(camera.model_dump())

    @staticmethod
    def delete_camera(camera_id: str):
        result = camera_collection.delete_one({"id": camera_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Camera not found")
