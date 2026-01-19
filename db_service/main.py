from fastapi import FastAPI, HTTPException, Query, Body
from typing import List, Optional
import db
from models import Record
from pydantic import BaseModel

app = FastAPI()

# --- Settings ---

class SettingsUpdate(BaseModel):
    memory: int
    sensitivity: float

@app.get("/settings")
def get_settings():
    return db.get_settings()

@app.post("/settings")
def update_settings(settings: SettingsUpdate):
    db.update_settings(settings.memory, settings.sensitivity)
    return {"status": "ok"}

# --- Cameras ---

class Camera(BaseModel):
    id: str
    ip: str

@app.get("/cameras")
def get_cameras():
    return db.fetch_camera_urls()

@app.get("/cameras/all")
def get_all_cameras():
    return db.get_cameras()

@app.post("/cameras")
def add_camera(camera: Camera):
    success = db.add_camera(camera.model_dump())
    if not success:
        raise HTTPException(status_code=400, detail="Camera ID already exists")
    return {"status": "created"}

@app.delete("/cameras/{id}")
def delete_camera(id: str):
    success = db.delete_camera(id)
    if not success:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"status": "deleted"}

# --- Notifications ---

@app.post("/notifications")
def add_notification(record: Record):
    result = db.add_notification(record)
    return result # Returns dict or str id

@app.get("/notifications/active")
def get_active_notifications():
    return db.get_active_notifications()

@app.post("/notifications/{id}/close")
def close_notification(id: str):
    count = db.close_notification(id)
    return {"matched_count": count}

@app.delete("/notifications/{id}")
def delete_notification(id: str):
    db.delete_notification(id)
    return {"status": "deleted"}

@app.post("/notifications/delete-batch")
def delete_notifications_by_ids(ids: List[str]):
    count = db.delete_notifications_by_ids(ids)
    return {"deleted_count": count}

@app.post("/notifications/clear-all")
def clear_all_notifications():
    count = db.clear_all_notifications()
    return {"modified_count": count}

@app.get("/notifications/by-date")
def get_notifications_by_date(
    start_date: str,
    end_date: str,
    skip: int = 0,
    limit: int = 12,
    label_list: Optional[List[str]] = Query(None)
):
    return db.get_notifications_by_date(start_date, end_date, skip, limit, label_list)

@app.get("/notifications/count")
def get_document_count(start_time: str, end_time: str):
    return db.get_document_count(start_time, end_time)

@app.get("/notifications/by-session/{session_id}")
def get_notifications_by_session(
    session_id: str,
    skip: int = 0,
    limit: int = 12,
    label_list: Optional[List[str]] = Query(None)
):
    return db.get_notifications_by_session(session_id, skip, limit, label_list)

@app.get("/notifications/count-by-session/{session_id}")
def get_notification_count_by_session(session_id: str):
    return db.get_notification_count(session_id)

@app.get("/notifications/{id}")
def get_notification_by_id(id: str):
    res = db.get_notification_by_id(id)
    if res is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return res

@app.get("/notifications/{id}/around")
def get_notifications_around_id(id: str, limit: int = 3):
    return db.get_notifications_around_id(id, limit)


# --- Detection Sessions ---

class SessionStart(BaseModel):
    camera_id: str

@app.post("/detection-sessions")
def add_detection_session(data: SessionStart):
    return db.add_detection_session(data.camera_id)

@app.get("/detection-sessions")
def get_detection_sessions_with_pagination(skip: int = 0, limit: int = 10):
    sessions, total = db.get_detection_sessions_with_pagination(skip, limit)
    return {"sessions": sessions, "total_count": total}

@app.get("/detection-sessions/all")
def get_all_detection_sessions():
    return db.get_all_detection_sessions()

@app.get("/detection-sessions/active")
def get_active_sessions():
    return db.get_active_sessions()

@app.get("/detection-sessions/{id}")
def get_detection_session_by_id(id: str):
    res = db.get_detection_session_by_id(id)
    if res is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return res

@app.post("/detection-sessions/{id}/end")
def update_detection_session_end(id: str):
    db.update_detection_session_end(id)
    return {"status": "updated"}

@app.post("/detection-sessions/update-last-open")
def update_last_open_session(data: SessionStart):
    db.update_last_open_session(data.camera_id)
    return {"status": "updated"}

@app.delete("/detection-sessions/{id}")
def delete_detection_session_and_related(id: str):
    count = db.delete_detection_session_and_related(id)
    return {"deleted_count": count}

# --- Maintenance ---

@app.delete("/all")
def delete_all(start_date: str, end_date: str):
    count = db.delete_all(start_date, end_date)
    return {"deleted_count": count}

@app.get("/health")
def health_check():
    status = db.test_mongodb_connection()
    if status:
        return {"status": "connected"}
    else:
        raise HTTPException(status_code=500, detail="Database connection failed")
