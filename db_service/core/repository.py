
from .database import get_db
from bson.objectid import ObjectId
from datetime import datetime
from typing import List, Optional, Dict
from .models import Record, DetectionSession

def get_notifications_collection():
    return get_db()["notifications"]

def get_detection_sessions_collection():
    return get_db()["detection_sessions"]

def get_settings_collection():
    return get_db()["system_settings"]

def get_cameras_collection():
    return get_db()["cameras"]


# --- Notifications ---

def add_notification(record_data: dict) -> str:
    # Ensure ID is not in data if it's meant to be auto-generated or handle it
    if "id" in record_data and record_data["id"]:
         # If coming from pydantic alias
         pass

    # Convert string dates back to datetime if needed, though Pydantic handles it usually.
    # But here we receive a dict from the route handler.
    if isinstance(record_data.get("time"), str):
        record_data["time"] = datetime.fromisoformat(record_data["time"])

    result = get_notifications_collection().insert_one(record_data)
    return str(result.inserted_id)

def get_active_notifications():
    return list(get_notifications_collection().find({"status": "active"}))

def get_notifications_by_date(start_date, end_date, skip=0, limit=12, label_list=None):
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    query = {"time": {"$gte": start_date, "$lte": end_date}}

    if label_list:
        label_exists_conditions = [
            {f"labels.{label}": {"$exists": True}} for label in label_list
        ]
        # Logic from original api/db.py
        not_other_labels_condition = {
            "labels": {
                "$not": {
                    "$elemMatch": {
                        "$and": [
                            {str(label): {"$exists": False}} for label in label_list
                        ]
                    }
                }
            }
        }
        query["$and"] = [*label_exists_conditions, not_other_labels_condition]

    return list(get_notifications_collection().find(query).skip(skip).limit(limit))

def get_notification_by_id(notification_id: str):
    try:
        return get_notifications_collection().find_one({"_id": ObjectId(notification_id)})
    except:
        return None

def close_notification(notification_id: str):
    result = get_notifications_collection().update_one(
        {"_id": ObjectId(notification_id)}, {"$set": {"status": "closed"}}
    )
    return result.matched_count

def delete_notification(notification_id: str):
    return get_notifications_collection().find_one_and_delete(
        {"_id": ObjectId(notification_id)}
    )

def delete_notifications_by_ids(notification_ids: List[str]):
    object_ids = [ObjectId(id) for id in notification_ids]
    return get_notifications_collection().delete_many({"_id": {"$in": object_ids}})

def clear_all_notifications():
    result = get_notifications_collection().update_many(
        {"status": "active"}, {"$set": {"status": "closed"}}
    )
    return result.modified_count

def delete_all_notifications_by_date(start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    # Find first to get image urls (caller needs them to delete files)
    # But wait, the db service shouldn't know about file system presumably?
    # The requirement says "Veritabanı işlemlerini ayrı bir servis haline getirerek".
    # File deletion logic is in api/db.py currently.
    # The DB service should returns the deleted records or image URLs so the caller can delete files.

    notifications = list(get_notifications_collection().find({"time": {"$gte": start_date, "$lte": end_date}}))
    result = get_notifications_collection().delete_many({"time": {"$gte": start_date, "$lte": end_date}})
    return notifications, result.deleted_count

def get_notifications_by_session(session_id: str, skip=0, limit=12, label_list=None):
    query = {"session_id": session_id}
    if label_list:
        or_conditions = []
        for label_id in label_list:
            condition = {"labels": {"$elemMatch": {label_id: {"$exists": True}}}}
            or_conditions.append(condition)
        if or_conditions:
            query["$or"] = or_conditions

    return list(get_notifications_collection().find(query).sort("time", -1).skip(skip).limit(limit))

def get_notification_count(session_id: str):
    return get_notifications_collection().count_documents({"session_id": session_id})

def get_document_count(start_time, end_time):
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)
    return get_notifications_collection().count_documents({"time": {"$gte": start_time, "$lt": end_time}})

def get_notifications_around_id(notification_id: str, limit: int):
    try:
        center_notification = get_notifications_collection().find_one({"_id": ObjectId(notification_id)})
        if not center_notification:
            return []

        center_time = center_notification["time"]

        before = list(get_notifications_collection().find(
            {"time": {"$lt": center_time}},
            sort=[("time", -1)],
            limit=limit//2
        ))
        after = list(get_notifications_collection().find(
            {"time": {"$gt": center_time}},
            sort=[("time", 1)],
            limit=limit//2
        ))

        return before[::-1] + [center_notification] + after
    except:
        return []

# --- Sessions ---

def add_detection_session(camera_id: str):
    session_data = {
        "camera_id": camera_id,
        "start": datetime.now(), # Store as datetime object
        "end": None,
        "record_count": None,
    }
    result = get_detection_sessions_collection().insert_one(session_data)
    return str(result.inserted_id)

def update_detection_session_end(session_id: str):
    record_count = get_notification_count(session_id)
    get_detection_sessions_collection().update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"end": datetime.now(), "record_count": record_count}},
    )

def get_detection_sessions_with_pagination(skip=0, limit=10):
    total_count = get_detection_sessions_collection().count_documents({})
    sessions = list(get_detection_sessions_collection().find().sort("start", -1).skip(skip).limit(limit))
    return sessions, total_count

def get_detection_session_by_id(session_id: str):
    try:
        return get_detection_sessions_collection().find_one({"_id": ObjectId(session_id)})
    except:
        return None

def delete_detection_session(session_id: str):
    try:
        return get_detection_sessions_collection().delete_one({"_id": ObjectId(session_id)})
    except:
        return None

def get_active_sessions():
    return list(get_detection_sessions_collection().find({"end": None}))

# --- Settings ---
def get_settings():
    settings_doc = get_settings_collection().find_one({"_id": "global_settings"})
    if settings_doc:
        return {
            "memory": settings_doc.get("memory", 5),
            "sensitivity": settings_doc.get("sensitivity", 0.2),
        }
    return {"memory": 5, "sensitivity": 0.2}

def update_settings(memory: int, sensitivity: float):
    get_settings_collection().update_one(
        {"_id": "global_settings"},
        {"$set": {"memory": memory, "sensitivity": sensitivity}},
        upsert=True,
    )

# --- Cameras ---
def fetch_camera_urls():
    return [cam["ip"] for cam in get_cameras_collection().find()]
