
from typing import List
from datetime import datetime
from services.core.db_client import db_client

# Define Record class locally for type hinting/usage in services if needed,
# or just pass dicts. Original services/core/db.py had Record model.
# Services likely import Record from here.

from pydantic import BaseModel, Field

class Record(BaseModel):
    frame_count: int
    labels: List[dict]
    image_url: str
    time: datetime
    status: str = "active"
    camera_id: str
    session_id: str
    # id field might be needed if creating with specific ID, usually not.

    class Config:
        populate_by_name = True

def fetch_camera_urls() -> List[str]:
    return db_client.fetch_camera_urls()

def add_notification(record: Record) -> str:
    # Convert record to dict
    data = record.model_dump(by_alias=True, exclude={"id"})
    # Handle datetime serialization if client doesn't (requests json arg handles basic types, but datetime?)
    # requests json serializer might not handle datetime.
    if isinstance(data.get("time"), datetime):
        data["time"] = data["time"].isoformat()

    # Client add_notification expects dict
    result = db_client.add_notification(data)
    # Result is just the string ID from my service implementation?
    # Check api/db_client.py: `return self._post("/notifications", json=record)`
    # Check db_service/routes/api.py: returns `add_notification(record)` which returns str.
    return result

def add_detection_session(camera_id: str) -> str:
    return db_client.add_detection_session(camera_id)

def get_notification_count(session_id: str) -> int:
    # I didn't add this to client?
    # Check api/db_client.py. `get_notification_count` is in `read_session_notification_count`?
    # db_service has `read_session_notification_count`.
    # I should update services/core/db_client.py to include this if needed.
    # But wait, `update_last_open_session` uses it.
    pass

def update_last_open_session(camera_id: str):
    # This logic was: find last open session, update end time and record count.
    # db_client doesn't have this.
    # I can implement it by:
    # 1. get_active_sessions()
    # 2. filter for camera_id
    # 3. update_detection_session_end(session_id)

    sessions = db_client.get_active_sessions()
    # Sort by start time desc?
    # Assuming list is returned.

    # Filter for camera
    cam_sessions = [s for s in sessions if s.get("camera_id") == camera_id]

    # Sort by start desc
    cam_sessions.sort(key=lambda x: x.get("start", ""), reverse=True)

    if cam_sessions:
        last_session = cam_sessions[0]
        db_client.update_detection_session_end(last_session["_id"])

def update_detection_session_end(session_id: str):
    db_client.update_detection_session_end(session_id)

def get_settings():
    return db_client.get_settings()
