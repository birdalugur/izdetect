import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import SON
from datetime import datetime
from typing import List, Optional, Tuple
from config import Config
from models import Record

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]
notifications_collection = db["notifications"]
detection_sessions_collection = db["detection_sessions"]
settings_collection = db["system_settings"]
camera_collection = db["cameras"]

# --- From services/core/db.py ---

def fetch_camera_urls() -> List[str]:
    """Fetch all camera IP addresses from the database."""
    # Using the global client instead of creating new one
    urls = [cam["ip"] for cam in camera_collection.find()]
    return urls

def get_cameras() -> List[dict]:
    cameras = list(camera_collection.find())
    return [{"id": cam["id"], "ip": cam["ip"]} for cam in cameras]

def add_camera(camera_data: dict):
    if camera_collection.find_one({"id": camera_data["id"]}):
        return False
    camera_collection.insert_one(camera_data)
    return True

def delete_camera(camera_id: str) -> bool:
    result = camera_collection.delete_one({"id": camera_id})
    return result.deleted_count > 0

def add_notification(record: Record) -> dict:
    insert_data = record.model_dump(by_alias=True, exclude={"id"})
    result = notifications_collection.insert_one(insert_data)
    insert_data["_id"] = str(result.inserted_id)
    return insert_data

def add_detection_session(camera_id: str) -> str:
    session_data = {
        "camera_id": camera_id,
        "start": datetime.now().isoformat(),
        "end": None,
        "record_count": None,
    }
    result = detection_sessions_collection.insert_one(session_data)
    return str(result.inserted_id)

def get_notification_count(session_id: str) -> int:
    return notifications_collection.count_documents({"session_id": session_id})

def update_last_open_session(camera_id: str):
    last_session = detection_sessions_collection.find_one(
        {"camera_id": camera_id, "end": None},
        sort=SON([("start", -1)]),
    )

    if last_session:
        session_id = str(last_session["_id"])
        record_count = get_notification_count(session_id)

        detection_sessions_collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"end": datetime.now().isoformat(), "record_count": record_count}},
        )

def update_detection_session_end(session_id: str):
    record_count = get_notification_count(session_id)
    detection_sessions_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"end": datetime.now().isoformat(), "record_count": record_count}},
    )

def test_mongodb_connection():
    try:
        db.command("ping")
        print("MongoDB bağlantisi başarili!")
        return True
    except Exception as e:
        print(f"MongoDB bağlanti hatasi: {e}")
        return False

# --- From api/db.py ---

def get_settings():
    settings_doc = settings_collection.find_one({"_id": "global_settings"})
    if settings_doc:
        return {
            "memory": settings_doc.get("memory", 5),
            "sensitivity": settings_doc.get("sensitivity", 0.2),
        }
    else:
        return {"memory": 5, "sensitivity": 0.2}

def update_settings(memory: int, sensitivity: float):
    settings_collection.update_one(
        {"_id": "global_settings"},
        {"$set": {"memory": memory, "sensitivity": sensitivity}},
        upsert=True,
    )

def get_detection_sessions_with_pagination(
    skip: int = 0, limit: int = 10
) -> Tuple[List[dict], int]:
    total_count = detection_sessions_collection.count_documents({})

    sessions = list(
        detection_sessions_collection.find().sort("start", -1).skip(skip).limit(limit)
    )

    for session in sessions:
        session["_id"] = str(session["_id"])
        session_id = session["_id"]
        # Optimizing: using the count function already defined
        session["record_count"] = notifications_collection.count_documents(
            {"session_id": session_id}
        )
        for key in ["start", "end"]:
            if key in session and isinstance(session[key], datetime):
                session[key] = session[key].isoformat()

    return sessions, total_count

def get_all_detection_sessions():
    sessions = list(detection_sessions_collection.find().sort("start", -1))
    for session in sessions:
        session["_id"] = str(session["_id"])
        for key in ["start", "end"]:
            if key in session and isinstance(session[key], datetime):
                session[key] = session[key].isoformat()
    return sessions

def get_active_sessions():
    sessions = list(detection_sessions_collection.find({"end": None}))
    for session in sessions:
        session["_id"] = str(session["_id"])
        if isinstance(session["start"], datetime):
            session["start"] = session["start"].isoformat()
    return sessions

def get_active_notifications():
    notifications = list(notifications_collection.find({"status": "active"}))
    for notification in notifications:
        notification["_id"] = str(notification["_id"])
        for key, value in notification.items():
            if isinstance(value, datetime):
                notification[key] = value.isoformat()
    return notifications

def close_notification(notification_id):
    result = notifications_collection.update_one(
        {"_id": ObjectId(notification_id)}, {"$set": {"status": "closed"}}
    )
    return result.matched_count

def delete_image(image_filename):
    if image_filename:
        image_path = os.path.join(Config.OUTPUT_FOLDER, image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

def delete_notification(notification_id: str):
    notification = notifications_collection.find_one_and_delete(
        {"_id": ObjectId(notification_id)}
    )

    if not notification:
        return None

    image_filename = notification.get("image_url")
    delete_image(image_filename)
    return

def delete_notifications_by_ids(notification_ids: List[str]):
    object_ids = [ObjectId(id) for id in notification_ids]
    notifications = list(notifications_collection.find({"_id": {"$in": object_ids}}))

    for notification in notifications:
        image_filename = notification.get("image_url")
        delete_image(image_filename)

    result = notifications_collection.delete_many({"_id": {"$in": object_ids}})
    return result.deleted_count

def delete_detection_session_and_related(session_id: str) -> int:
    try:
        obj_id = ObjectId(session_id)
    except Exception:
        return 0

    notifications = list(
        notifications_collection.find({"session_id": session_id}, {"image_url": 1})
    )
    for n in notifications:
        delete_image(n.get("image_url"))
    notifications_collection.delete_many({"session_id": session_id})

    result = detection_sessions_collection.delete_one({"_id": obj_id})
    return result.deleted_count

def delete_all(start_date, end_date):
    # Expecting datetime objects or strings.
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    notifications = list(
        notifications_collection.find({"time": {"$gte": start_date, "$lte": end_date}})
    )
    deleted_session_ids = {n["session_id"] for n in notifications}

    for n in notifications:
        delete_image(n.get("image_url"))

    result = notifications_collection.delete_many(
        {"time": {"$gte": start_date, "$lte": end_date}}
    )

    for session_id in deleted_session_ids:
        remaining = notifications_collection.count_documents({"session_id": session_id})
        if remaining == 0:
            detection_sessions_collection.delete_one({"_id": ObjectId(session_id)})

    return result.deleted_count

def clear_all_notifications():
    result = notifications_collection.update_many(
        {"status": "active"}, {"$set": {"status": "closed"}}
    )
    return result.modified_count

def get_notifications_by_date(
    start_date, end_date, skip=0, limit=12, label_list: Optional[List[str]] = None
):
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    query = {"time": {"$gte": start_date, "$lte": end_date}}

    if label_list:
        label_exists_conditions = [
            {f"labels.{label}": {"$exists": True}} for label in label_list
        ]
        # This query logic from existing db.py looks complex but I'll preserve it
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

    notifications = list(notifications_collection.find(query).skip(skip).limit(limit))

    for notification in notifications:
        notification["_id"] = str(notification["_id"])
        for key, value in notification.items():
            if isinstance(value, datetime):
                notification[key] = value.isoformat()

    return notifications

def get_document_count(start_time, end_time):
    if isinstance(start_time, str):
        start_dt = datetime.fromisoformat(start_time)
    else:
        start_dt = start_time

    if isinstance(end_time, str):
        end_dt = datetime.fromisoformat(end_time)
    else:
        end_dt = end_time

    count = notifications_collection.count_documents({
        "time": {
            "$gte": start_dt,
            "$lt": end_dt
            }})
    return count

def get_notifications_by_session(
    session_id: str,
    skip: int = 0,
    limit: int = 12,
    label_list: Optional[List[str]] = None,
) -> List[dict]:
    query = {"session_id": session_id}

    if label_list:
        or_conditions = []
        for label_id in label_list:
            condition = {"labels": {"$elemMatch": {label_id: {"$exists": True}}}}
            or_conditions.append(condition)
        
        if or_conditions:
            query["$or"] = or_conditions

    notifications = list(
        notifications_collection.find(query)
        .sort("time", -1)
        .skip(skip)
        .limit(limit)
    )

    for notification in notifications:
        notification["_id"] = str(notification["_id"])
        for key, value in notification.items():
            if isinstance(value, datetime):
                notification[key] = value.isoformat()

    return notifications

def get_notification_by_id(notification_id: str) -> Optional[dict]:
    try:
        notification = notifications_collection.find_one({"_id": ObjectId(notification_id)})
        if notification:
            notification["_id"] = str(notification["_id"])
            for key, value in notification.items():
                if isinstance(value, datetime):
                    notification[key] = value.isoformat()
        return notification
    except:
        return None

def get_notifications_around_id(notification_id: str, limit: int = 3) -> List[dict]:
    try:
        center_notification = notifications_collection.find_one({"_id": ObjectId(notification_id)})
        if not center_notification:
            return []

        center_time = center_notification["time"]

        before = list(notifications_collection.find(
            {"time": {"$lt": center_time}},
            sort=[("time", -1)],
            limit=limit//2
        ))
        after = list(notifications_collection.find(
            {"time": {"$gt": center_time}},
            sort=[("time", 1)],
            limit=limit//2
        ))

        notifications = before[::-1] + [center_notification] + after

        for notification in notifications:
            notification["_id"] = str(notification["_id"])
            for key, value in notification.items():
                if isinstance(value, datetime):
                    notification[key] = value.isoformat()

        return notifications
    except:
        return []

def get_detection_session_by_id(session_id: str) -> Optional[dict]:
    try:
        session = detection_sessions_collection.find_one({"_id": ObjectId(session_id)})
        if not session:
            return None
            
        session["_id"] = str(session["_id"])
        session["record_count"] = notifications_collection.count_documents(
            {"session_id": session_id}
        )
        
        for key in ["start", "end"]:
            if key in session and isinstance(session[key], datetime):
                session[key] = session[key].isoformat()
                
        return session
    except:
        return None
