import os
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from config import Config
from infrastructure.mongo_repository import MongoDetectionRepository

# Singleton repository instance
repository = MongoDetectionRepository()

def get_settings():
    return repository.get_settings()

def update_settings(memory: int, sensitivity: float):
    return repository.update_settings(memory, sensitivity)

def get_detection_sessions_with_pagination(skip: int = 0, limit: int = 10) -> Tuple[List[dict], int]:
    return repository.get_detection_sessions_with_pagination(skip, limit)

def get_all_detection_sessions():
    return repository.get_all_detection_sessions()

def get_active_sessions():
    return repository.get_active_sessions()

def get_active_notifications():
    return repository.get_active_notifications()

def close_notification(notification_id):
    return repository.close_notification(notification_id)

def delete_image(image_filename):
    if image_filename:
        image_path = os.path.join(Config.OUTPUT_FOLDER, image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

def delete_notification(notification_id: str):
    notification = repository.delete_notification(notification_id)
    if notification:
        image_filename = notification.get("image_url")
        delete_image(image_filename)

def delete_notifications_by_ids(notification_ids: List[str]):
    result, notifications = repository.delete_notifications_by_ids(notification_ids)
    for notification in notifications:
        image_filename = notification.get("image_url")
        delete_image(image_filename)
    return result

def delete_detection_session_and_related(session_id: str) -> int:
    try:
        notifications = repository.get_notifications_by_session_id(session_id)
        for n in notifications:
            delete_image(n.get("image_url"))
        repository.delete_notifications_by_session_id(session_id)
        result = repository.delete_session(session_id)
        return result.deleted_count
    except Exception:
        return 0

def delete_all(start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    query = {"time": {"$gte": start_date, "$lte": end_date}}
    notifications = repository.delete_notifications(query)

    deleted_session_ids = {n["session_id"] for n in notifications}

    for n in notifications:
        delete_image(n.get("image_url"))

    # Cleanup sessions
    for session_id in deleted_session_ids:
        remaining = repository.count_notifications({"session_id": session_id})
        if remaining == 0:
            repository.delete_session(session_id)

    return len(notifications)

def clear_all_notifications():
    result = repository.update_notifications_status({"status": "active"}, "closed")
    return result.modified_count

def get_notifications_by_date(start_date, end_date, skip=0, limit=12, label_list: Optional[List[str]] = None):
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    query = {"time": {"$gte": start_date, "$lte": end_date}}

    if label_list:
        label_exists_conditions = [
            {f"labels.{label}": {"$exists": True}} for label in label_list
        ]
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

    return repository.find_notifications(query, skip=skip, limit=limit)

def get_document_count(start_time, end_time):
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    return repository.count_notifications({"time": {"$gte": start_dt, "$lt": end_dt}})

def get_notifications_by_session(session_id: str, skip: int = 0, limit: int = 12, label_list: Optional[List[str]] = None):
    query = {"session_id": session_id}
    if label_list:
        or_conditions = []
        for label_id in label_list:
            condition = {"labels": {"$elemMatch": {label_id: {"$exists": True}}}}
            or_conditions.append(condition)
        if or_conditions:
            query["$or"] = or_conditions

    return repository.find_notifications(query, skip=skip, limit=limit, sort=[("time", -1)])

def get_notification_by_id(notification_id: str):
    return repository.get_notification(notification_id)

def get_notifications_around_id(notification_id: str, limit: int = 3) -> List[dict]:
    try:
        center_notification = repository.get_notification(notification_id)
        if not center_notification:
            return []

        # center_notification["time"] is ISO string from repository format
        center_time = datetime.fromisoformat(center_notification["time"])

        before = repository.find_notifications(
            {"time": {"$lt": center_time}}, sort=[("time", -1)], limit=limit//2
        )
        after = repository.find_notifications(
            {"time": {"$gt": center_time}}, sort=[("time", 1)], limit=limit//2
        )

        return before[::-1] + [center_notification] + after
    except:
        return []

def get_detection_session_by_id(session_id: str):
    session = repository.get_detection_session(session_id)
    if session:
        session["record_count"] = repository.get_notification_count(session_id)
    return session
