import requests
import os
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from bson.objectid import ObjectId

# Replicate Record model from db_service/models.py to ensure compatibility
class Record(BaseModel):
    frame_count: int
    labels: List[dict]
    image_url: str
    time: datetime
    status: str = "active"
    camera_id: str
    session_id: str
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="id")

    class Config:
        populate_by_name = True

DB_SERVICE_URL = os.environ.get("DB_SERVICE_URL", "http://db-service:8000")

def fetch_camera_urls() -> List[str]:
    resp = requests.get(f"{DB_SERVICE_URL}/cameras")
    resp.raise_for_status()
    return resp.json()

def get_settings():
    resp = requests.get(f"{DB_SERVICE_URL}/settings")
    resp.raise_for_status()
    return resp.json()

def add_notification(record: Record) -> dict:
    resp = requests.post(f"{DB_SERVICE_URL}/notifications", json=record.model_dump(mode='json', by_alias=True))
    resp.raise_for_status()
    return resp.json()

def add_detection_session(camera_id: str) -> str:
    resp = requests.post(f"{DB_SERVICE_URL}/detection-sessions", json={"camera_id": camera_id})
    resp.raise_for_status()
    return resp.json()

def update_detection_session_end(session_id: str):
    requests.post(f"{DB_SERVICE_URL}/detection-sessions/{session_id}/end").raise_for_status()
