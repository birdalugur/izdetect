from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from typing import List
import redis
import json

client = MongoClient("mongodb://localhost:27017/")
db = client["object_detection"]
notifications_collection = db["notifications"]
selected_label_map = {1: "insan", 2: "arac", 3: "hayvan"}


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


def publish_to_redis(data):
    new_data = prepare_notification_data(**data)

    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    try:
        message = json.dumps(new_data)
        redis_client.publish("event_channel", message)
    except Exception as e:
        print(f"Error publishing to Redis: {e}")


def prepare_notification_data(
    frame_count: int,
    labels: List[dict],
    image_url: str,
    time: float,
    status: str,
    _id: str,
    camera_id: str,
) -> dict:
    mapped_labels = [
        {selected_label_map.get(int(k), k): v for k, v in label.items()}
        for label in labels
    ]

    return {
        "_id": str(_id),
        "frame_count": frame_count,
        "labels": mapped_labels,
        "image_url": image_url,
        "time": time.isoformat(),
        "status": status,
        "camera_id": camera_id,
    }


def add_notification(record: Record) -> str:
    insert_data = record.model_dump(by_alias=True, exclude={"id"})
    _ = notifications_collection.insert_one(insert_data)

    publish_to_redis(insert_data)

    return insert_data


if __name__ == "__main__":
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
