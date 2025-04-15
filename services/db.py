from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from typing import List
import os

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
    camera_id: int
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
