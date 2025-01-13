from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from typing import List

import aioredis
import asyncio
import json


client = MongoClient("mongodb://localhost:27017/")
db = client["object_detection"]
notifications_collection = db["notifications"]
selected_label_map = {1: "insan", 2: "arac", 3: "hayvan"}


class Notification(BaseModel):
    frame_count: int
    labels: List[dict]
    image_url: str
    time: datetime
    status: str = "active"
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="id")

    class Config:
        populate_by_name = True


async def publish_to_redis(data):
    data = prepare_notification_data(**data)

    redis = await aioredis.from_url("redis://localhost:6379")
    try:
        message = json.dumps(data)
        await redis.publish("event_channel", message)
        await asyncio.sleep(0.1)
    finally:
        await redis.close()


def prepare_notification_data(
    frame_count: int,
    labels: List[dict],
    image_url: str,
    time: float,
    status: str,
    _id: str,
) -> dict:
    mapped_labels = []
    for label in labels:
        mapped_labels.append(
            {selected_label_map.get(int(k), k): v for k, v in label.items()}
        )

    return {
        "_id": str(_id),
        "frame_count": frame_count,
        "labels": mapped_labels,
        "image_url": image_url,
        "time": time.isoformat(),
        "status": status,
    }


def add_notification_toDB(
    frame_count: int, labels: List[dict], image_url: str, frame_time: float
) -> str:
    """
    Yeni bir notification kaydi oluşturur ve MongoDB'ye ekler.

    Args:
        frame_count (int): Frame sayisi
        labels (List[dict]): Etiketler
        image_url (str): Resim URL'si
        frame_time (float): Zaman damgasi

    Returns:
        str: Eklenen belgenin MongoDB ID'si
    """
    record = Notification(
        frame_count=frame_count,
        labels=labels,
        image_url=image_url,
        time=datetime.fromtimestamp(frame_time),
    )

    insert_data = record.model_dump(by_alias=True, exclude={"id"})
    result = notifications_collection.insert_one(insert_data)

    asyncio.run(publish_to_redis(insert_data))

    return str(result.inserted_id)


if __name__ == "__main__":
    # Örnek veri
    frame_count = 10
    formatted_labels = [{"person": 2}, {"car": 1}]
    image_url = "http://example.com/image.jpg"
    frame_time = datetime.timestamp(datetime.now())

    notification_id = add_notification_toDB(
        frame_count, formatted_labels, image_url, frame_time
    )
    print("Inserted ID:", notification_id)
