from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime


client = MongoClient("mongodb://localhost:27017/")
# client = MongoClient("mongodb:27017") # for docker
db = client["object_detection"]
notifications_collection = db["notifications"]


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
