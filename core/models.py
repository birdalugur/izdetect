from pydantic import BaseModel, Field
from typing import List, Optional
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
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="id")

    class Config:
        populate_by_name = True
