from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from typing import List
import os
from bson import SON

selected_label_map = {1: "insan", 2: "arac", 3: "hayvan"}


def get_db():
    mongo_host = os.environ.get("MONGO_HOST", "localhost")
    mongo_port = os.environ.get("MONGO_PORT", "27017")
    mongo_user = os.environ.get("MONGO_USER", "")
    mongo_pass = os.environ.get("MONGO_PASS", "")
    mongo_db = os.environ.get("MONGO_DB", "object_detection")

    if mongo_user and mongo_pass:
        mongo_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/"
    else:
        mongo_url = f"mongodb://{mongo_host}:{mongo_port}/"

    client = MongoClient(mongo_url)
    return client[mongo_db], client


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


def add_notification(record: Record) -> str:
    db, client = get_db()
    notifications_collection = db["notifications"]

    insert_data = record.model_dump(by_alias=True, exclude={"id"})
    _ = notifications_collection.insert_one(insert_data)
    client.close()
    return insert_data


def add_detection_session(camera_id: str) -> str:
    """Insert a new detection session record with start timestamp."""
    db, client = get_db()
    detection_sessions_collection = db["detection_sessions"]

    session_data = {
        "camera_id": camera_id,
        "start": datetime.now().isoformat(),
        "end": None,
        "record_count": None,
    }
    result = detection_sessions_collection.insert_one(session_data)
    client.close()
    return str(result.inserted_id)


def get_notification_count(session_id: str) -> int:
    """Belirtilen session_id'ye sahip notification kayıtlarının sayısını döndürür."""
    db, client = get_db()
    notifications_collection = db["notifications"]

    count = notifications_collection.count_documents({"session_id": session_id})
    client.close()
    return count


def update_last_open_session(camera_id: str):
    """End timestamp'i olmayan en son oturumu bitiş zamanı ve kayıt sayısı ile günceller."""
    db, client = get_db()
    detection_sessions_collection = db["detection_sessions"]

    # En son açık oturumu al
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

    client.close()


def update_detection_session_end(session_id: str):
    """Update the end timestamp and record count of a detection session."""
    db, client = get_db()
    detection_sessions_collection = db["detection_sessions"]

    record_count = get_notification_count(session_id)

    detection_sessions_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"end": datetime.now().isoformat(), "record_count": record_count}},
    )
    client.close()


def test_mongodb_connection():
    try:
        db, client = get_db()
        db.command("ping")
        print("MongoDB bağlantisi başarili!")
        client.close()
        return True
    except Exception as e:
        print(f"MongoDB bağlanti hatasi: {e}")
        return False


if __name__ == "__main__":
    test_mongodb_connection()
    # Örnek veri
    frame_count = 10
    formatted_labels = [{"person": 2}, {"car": 1}]
    image_url = "http://example.com/image.jpg"
    frame_time = datetime.now()

    record = Record(
        frame_count=frame_count,
        labels=formatted_labels,
        image_url=image_url,
        time=frame_time,
        camera_id=123,
    )

    notification_id = add_notification(record)
    print("Inserted ID:", notification_id)
