
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson.objectid import ObjectId

class Record(BaseModel):
    frame_count: int
    labels: List[dict]
    image_url: str
    time: datetime
    status: str = "active"
    camera_id: str
    session_id: str
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

class Notification(BaseModel):
    id: str = Field(alias="_id")
    frame_count: int
    labels: List[dict]
    image_url: str
    time: datetime
    status: str
    camera_id: str
    session_id: str

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

class DetectionSession(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    camera_id: str
    start: datetime
    end: Optional[datetime] = None
    record_count: Optional[int] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

class Settings(BaseModel):
    memory: int
    sensitivity: float
