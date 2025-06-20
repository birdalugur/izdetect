import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from typing import List, Optional, Tuple
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client["object_detection"]
notifications_collection = db["notifications"]
detection_sessions_collection = db["detection_sessions"]


def get_detection_sessions_with_pagination(
    skip: int = 0, limit: int = 10
) -> Tuple[List[dict], int]:
    """
    Detection sessions koleksiyonundaki verileri sayfalama ile getirir.

    Args:
        skip: Kaç kayıt atlanacak
        limit: Kaç kayıt getirileceği

    Returns:
        Tuple containing (sessions_list, total_count)
    """
    total_count = detection_sessions_collection.count_documents({})

    sessions = list(
        detection_sessions_collection.find().sort("start", -1).skip(skip).limit(limit)
    )

    for session in sessions:
        session["_id"] = str(session["_id"])
        for key in ["start", "end"]:
            if key in session and isinstance(session[key], datetime):
                session[key] = session[key].isoformat()

    return sessions, total_count


def get_all_detection_sessions():
    """
    detection_sessions koleksiyonundaki tüm verileri getirir.
    Bu fonksiyon geriye dönük uyumluluk için korunmuştur.
    """
    sessions = list(detection_sessions_collection.find().sort("start", -1))
    for session in sessions:
        session["_id"] = str(session["_id"])
        for key in ["start", "end"]:
            if key in session and isinstance(session[key], datetime):
                session[key] = session[key].isoformat()
    return sessions


def get_active_sessions():
    """
    Henüz bitiş zamanı olmayan (devam eden) detection oturumlarını getirir.
    """
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
    return result


def delete_detection_session_and_related(session_id: str) -> int:
    """
    Bir detection_session kaydını, ilişkili notification'ları ve bunların görsellerini siler.

    Args:
        session_id: Silinecek detection_session’ın string ObjectId’si

    Returns:
        Silinen detection_session adedi (0 | 1)
    """
    try:
        obj_id = ObjectId(session_id)
    except Exception:
        return 0

    # 1) İlgili notification’ları ve görselleri temizle
    notifications = list(
        notifications_collection.find({"session_id": session_id}, {"image_url": 1})
    )
    for n in notifications:
        delete_image(n.get("image_url"))
    notifications_collection.delete_many({"session_id": session_id})

    # 2) Detection session’ı sil
    result = detection_sessions_collection.delete_one({"_id": obj_id})
    return result.deleted_count


def delete_all(start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)
    result = notifications_collection.delete_many(
        {"time": {"$gte": start_date, "$lte": end_date}}
    )
    return result


def clear_all_notifications():
    result = notifications_collection.update_many(
        {"status": "active"}, {"$set": {"status": "closed"}}
    )
    return result.modified_count


def get_notifications_by_date(
    start_date, end_date, skip=0, limit=12, label_list: Optional[List[str]] = None
):
    """
    :param start_date: Başlangiç tarihi (ISO formatinda string veya datetime objesi)
    :param end_date: Bitiş tarihi (ISO formatinda string veya datetime objesi)
    :param skip: Kaç kayit atlanacak
    :param limit: Kaç kayit alinacak
    :param label_list: Filtrelenecek label ID'leri listesi (opsiyonel)
    :return: Belirtilen tarih araligindaki bildirimlerin listesi
    """
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

    notifications = list(notifications_collection.find(query).skip(skip).limit(limit))

    for notification in notifications:
        notification["_id"] = str(notification["_id"])
        for key, value in notification.items():
            if isinstance(value, datetime):
                notification[key] = value.isoformat()

    return notifications


def get_notifications_by_session(
    session_id: str,
    skip: int = 0,
    limit: int = 12,
    label_list: Optional[List[str]] = None,
) -> List[dict]:
    """
    Belirtilen session_id'ye göre bildirimleri getirir.

    Args:
        session_id: Bildirimlerin getirileceği session ID'si
        skip: Kaç kayıt atlanacak
        limit: Kaç kayıt alınacak
        label_list: Filtrelenecek label ID'leri listesi (opsiyonel)

    Returns:
        Belirtilen session_id ile ilişkili bildirimlerin listesi
    """
    query = {"session_id": session_id}

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

    notifications = list(notifications_collection.find(query).skip(skip).limit(limit))

    for notification in notifications:
        notification["_id"] = str(notification["_id"])
        for key, value in notification.items():
            if isinstance(value, datetime):
                notification[key] = value.isoformat()

    return notifications


if __name__ == "__main__":
    ds = get_notifications_by_session("6853c51e0d165f98edfe78f4", 0, 10, ["1", "2"])
    print(ds)
    print("length:", len(ds))