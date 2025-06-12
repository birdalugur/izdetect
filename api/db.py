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


def get_detection_sessions_with_pagination(skip: int = 0, limit: int = 10) -> Tuple[List[dict], int]:
    """
    Detection sessions koleksiyonundaki verileri sayfalama ile getirir.
    
    Args:
        skip: Kaç kayıt atlanacak
        limit: Kaç kayıt getirileceği
    
    Returns:
        Tuple containing (sessions_list, total_count)
    """
    # Total count for pagination info
    total_count = detection_sessions_collection.count_documents({})
    
    # Get paginated sessions, sorted by start time (newest first)
    sessions = list(
        detection_sessions_collection
        .find()
        .sort("start", -1)  # -1 for descending order (newest first)
        .skip(skip)
        .limit(limit)
    )
    
    # Process the sessions
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
        notification["_id"] = str(notification["_id"])  # ObjectId'yi stringe çevir
        for key, value in notification.items():
            if isinstance(value, datetime):  # Eğer datetime ise stringe çevir
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
        print(image_path)
        if os.path.exists(image_path):
            print(True)
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


def get_statistics():
    notifications = get_active_notifications()
    object_stats = {}
    for notification in notifications:
        for label in notification["labels"]:
            label_name, count = next(iter(label.items()))
            object_stats[label_name] = object_stats.get(label_name, 0) + int(count)
    return {"total_notifications": len(notifications), "object_stats": object_stats}


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

    # Eğer label filtresi varsa sorguya ekle
    if label_list:
        # Tüm label'ların var olduğunu kontrol et (string key olarak)
        label_exists_conditions = [
            {f"labels.{label}": {"$exists": True}} for label in label_list
        ]

        # Başka label olmadığını kontrol et (string key olarak)
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
    # start = "2025-02-01T00:00:00"
    # end = "2025-02-26T23:59:59"
    # records = get_notifications_by_date(start, end)
    # print(records)

    ds = get_all_detection_sessions()
    print(ds)

    das = get_active_sessions()
    print(das)