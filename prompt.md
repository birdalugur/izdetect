**Başlık:** Kod İyileştirme ve Optimizasyon Talebi  

**Açıklama:**  
Aşağıda verilen kodun işlevselliğini koruyarak daha okunabilir, etkili ve sürdürülebilir hale getirilmesini istiyorum. Lütfen aşağıdaki konulara odaklanarak iyileştirme yap:  

1. notify.py'de çağrılan add_notification_toDB aynı zamanda redis'e publish yapıyor. Bunları ayrı işlevlerde gerçekleştir.
2. db.py'de prepare_notification_data işlevine gerçekten ihtiyaç var mı? Pydantic modelini kullanarak kodu azaltma yapılabilir mi? Cevap evet ise düzenle.

notify.py:
import redis
import json
import uuid
import cv2
from datetime import datetime
from collections import Counter
from utils import draw_detection_with_det, decode_img
from db import add_notification_toDB

r = redis.StrictRedis(host="localhost", port=6379, decode_responses=False)

notified_object_ids = set()

selected_label = {1, 2, 3, 4, 6, 8, 18, 19, 20, 21}


def notify_objects(image_queue: str, detection_queue: str):
    count = 0
    while True:
        _, image_bytes = r.brpop(image_queue, timeout=0)
        _, detection_ids_bytes = r.brpop(detection_queue, timeout=0)

        if image_bytes and detection_ids_bytes:
            detection_ids = json.loads(detection_ids_bytes)

            # Hem notified_object_ids kontrolü hem de selected_label kontrolü
            filtered_detection_ids = [
                det
                for det in detection_ids
                if det[-2] not in notified_object_ids and det[-1] in selected_label
            ]

            if filtered_detection_ids:
                image_array = decode_img(image_bytes)
                for det in filtered_detection_ids:
                    det_id = det[-2]
                    if det_id not in notified_object_ids:
                        notified_object_ids.add(det_id)
                        draw_detection_with_det(image_array, det)
                    else:
                        continue

                label_counts = Counter(det[-1] for det in filtered_detection_ids)
                labels = [
                    {str(label_id): count} for label_id, count in label_counts.items()
                ]

                unique_id = str(uuid.uuid4()) + ".jpg"
                image_path = f"data/{unique_id}"
                cv2.imwrite(image_path, image_array)

                # TODO: count degeri frame okundugundaki değer olmali
                frame_count = count
                # TODO: frame_time degeri frame okundugu zamana ait olmali
                frame_time = datetime.timestamp(datetime.now())
                _ = add_notification_toDB(frame_count, labels, unique_id, frame_time)

            count += 1




db.py:
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
