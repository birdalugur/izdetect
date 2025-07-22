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

settings_collection = db["system_settings"]


def get_settings():
    settings_doc = settings_collection.find_one({"_id": "global_settings"})
    if settings_doc:
        return {
            "memory": settings_doc.get("memory", 5),
            "sensitivity": settings_doc.get("sensitivity", 0.2),
        }
    else:
        # Return defaults if not found
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
        session_id = session["_id"]
        session["record_count"] = notifications_collection.count_documents(
            {"session_id": session_id}
        )
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

    print(f"start date {start_date} end date {end_date}")

    # 1. Silinecek notification'ları al
    notifications = list(
        notifications_collection.find({"time": {"$gte": start_date, "$lte": end_date}})
    )
    deleted_session_ids = {n["session_id"] for n in notifications}

    # 2. Notification'ları ve görselleri sil
    for n in notifications:
        delete_image(n.get("image_url"))
    result = notifications_collection.delete_many(
        {"time": {"$gte": start_date, "$lte": end_date}}
    )

    # 3. Her session_id için hâlâ kayıt var mı kontrol et, yoksa session'ı sil
    for session_id in deleted_session_ids:
        remaining = notifications_collection.count_documents({"session_id": session_id})
        if remaining == 0:
            detection_sessions_collection.delete_one({"_id": ObjectId(session_id)})

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


def get_document_count(start_time, end_time):
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)

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
        # MongoDB query for array of objects: labels: [{"1": 10}, {"2": 2}]
        # We need to check if any object in labels array has the specified key
        or_conditions = []
        for label_id in label_list:
            # Check if labels array contains an object with this key
            condition = {"labels": {"$elemMatch": {label_id: {"$exists": True}}}}
            or_conditions.append(condition)
        
        if or_conditions:
            query["$or"] = or_conditions

    # Sort by time in descending order (newest first)
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
    """
    Tek bir bildirimi ID'sine göre getirir.

    Args:
        notification_id: Getirilecek bildirimin ID'si

    Returns:
        Bildirim verisi veya None
    """
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
    """
    Belirli bir bildirim ID'sinin etrafındaki bildirimleri getirir.
    Örneğin limit=3 için, verilen ID'nin öncesindeki 1 ve sonrasındaki 1 bildirimi getirir.

    Args:
        notification_id: Merkez bildirim ID'si
        limit: Toplam kaç bildirim getirileceği (tek sayı olmalı)

    Returns:
        Bildirimlerin listesi
    """
    try:
        # Önce merkez bildirimi bul
        center_notification = notifications_collection.find_one({"_id": ObjectId(notification_id)})
        if not center_notification:
            return []

        # Merkez bildirimin zamanını al
        center_time = center_notification["time"]

        # Önceki ve sonraki bildirimleri al
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

        # Sonuçları birleştir ve sırala
        notifications = before[::-1] + [center_notification] + after

        # ObjectId'leri string'e çevir ve datetime'ları format'la
        for notification in notifications:
            notification["_id"] = str(notification["_id"])
            for key, value in notification.items():
                if isinstance(value, datetime):
                    notification[key] = value.isoformat()

        return notifications
    except:
        return []


def get_detection_session_by_id(session_id: str) -> Optional[dict]:
    """
    Belirtilen session_id'ye göre tek bir detection session getirir.
    
    Args:
        session_id: Getirileceği session ID'si
        
    Returns:
        Session bilgisi veya None
    """
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


if __name__ == "__main__":
    ds = get_notifications_by_session("6853c51e0d165f98edfe78f4", 0, 10, ["1", "2"])
    print(ds)
    print("length:", len(ds))
