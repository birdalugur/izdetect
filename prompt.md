verilen talimatlara göre kodu güncelle veya yeni özellikler ekle.

açıklama:
aşağıda kodları verilen sistem video karelerini yakalar, bu kareler içindeki nesneleri tespit eder, nesneleri kareler arasında izler ve belirli nesne kategorilerinin tespit edilmesi durumunda bildirimler üretir. ikinci bir kamera kaynağını bu sisteme dahil edilmesi isteniyor.

talimatlar:
- her kamera kaynağının işlemi kendi processinde çalışmalıdır.
- kuyruk yapılarını dinamik hale getir.
- çoklu kamera senaryosunda karmaşaya yol açabilecek kod kısımlarını belirle ve bunları daha esnek ve geliştirilebilir hale getir.
- her bildirimin hangi kamera kaynağından geldiği bilinmelidir.

kodlar:
frame_producer.py:
import cv2
import redis
import time
from processing_timer import ProcessingTimer
from image_processor import ImageProcessor


class FrameProducer:
    def __init__(self, output_queue, url_key, redis_host="localhost", redis_port=6379):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.output_queue = output_queue
        self.url_key = url_key
        self.redis_client = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, decode_responses=True
        )
        self.video_source = None
        self.timer = ProcessingTimer()

    def get_camera_url(self):
        return self.redis_client.get(self.url_key)

    def check_stop_signal(self):
        stop_signal = self.redis_client.get("stop_signal")
        if stop_signal == "1":
            self.redis_client.delete("stop_signal")
            print("Stop signal received. Halting frame processing.")
            return True
        return False

    def capture_frames(self, encoding_method="binary"):
        while True:
            # Check for new camera URL
            new_video_source = self.get_camera_url()
            if new_video_source and new_video_source != self.video_source:
                self.video_source = new_video_source
                print(f"New camera URL received: {self.video_source}")
                self.redis_client.delete("camera_url")

            if not self.video_source:
                print("Waiting for a valid camera URL...")
                time.sleep(1)
                continue

            # Start capturing frames
            cap = cv2.VideoCapture(self.video_source)
            no_frame_count = 0
            self.timer.start("read")

            while True:
                if self.check_stop_signal():
                    break
                ret, frame = cap.read()
                if not ret:
                    no_frame_count += 1
                    print("No frames from camera, retrying...")
                    time.sleep(0.1)
                    if no_frame_count >= 5:
                        print("Camera disconnected, switching to URL wait mode.")
                        self.timer.stop("read")
                        self.timer.print_summary()
                        self.video_source = None
                        break
                    continue
                else:
                    no_frame_count = 0

                image_bytes = ImageProcessor.encode_img(
                    frame, encoding_method=encoding_method
                )
                self.redis_client.lpush(self.output_queue, image_bytes)

            # Release the camera and wait for a new URL
            cap.release()
            self.video_source = None
            print("All frames processed. Waiting for a new camera URL...")
            while not self.get_camera_url():
                time.sleep(1)


inference.py:
import time
import model
from typing import List
from redis_client import RedisClient
from image_processor import ImageProcessor


class Inference:
    def __init__(
        self,
        redis_client: RedisClient,
        input_queue: str,
        output_queue: str,
        image_bytes_queue: str,
    ):
        self.redis_client = redis_client
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.image_bytes_queue = image_bytes_queue
        self.idle_count = 0

    def process_single_frame(self, image_bytes: bytes):
        """Processes a single image frame."""
        image = ImageProcessor.decode_image(image_bytes)
        detections = model.process_frame(image)
        ImageProcessor.save_image_with_detections(image, detections)
        self.redis_client.push_to_queue(self.image_bytes_queue, [image_bytes])

    def process_batch_frames(self, image_bytes_list: List[bytes]):
        """Processes a batch of image frames."""
        images = ImageProcessor.decode_image_batch(image_bytes_list)
        detection_results = model.process_batch(images)
        serialized_results = ImageProcessor.serialize_detection_results(
            detection_results
        )
        self.redis_client.push_to_queue(self.output_queue, serialized_results)
        self.redis_client.push_to_queue(self.image_bytes_queue, image_bytes_list)

    def start(self):
        """Main loop to process frames from the Redis queue."""
        while True:
            image_bytes = self.redis_client.pop_from_queue(self.input_queue, 5)

            if image_bytes:
                self.idle_count = 0
                if isinstance(image_bytes, bytes):
                    self.process_single_frame(image_bytes)
                elif isinstance(image_bytes, list):
                    self.process_batch_frames(image_bytes)
            else:
                self.idle_count += 1
                print("Queue is empty, waiting...")
                time.sleep(1)

                if self.idle_count >= 5:
                    print("Queue is empty, entering sleep mode.")
                    time.sleep(5)

tracking.py:
import json
import numpy as np
import time
from typing import List
from sort import Sort
from redis_client import RedisClient


def watch_settings(processor):
    while True:
        try:
            memory = int(
                processor.redis_client.client.get("tracking:memory") or processor.memory
            )
            sensitivity = float(
                processor.redis_client.client.get("tracking:sensitivity")
                or processor.sensitivity
            )

            if memory != processor.memory or sensitivity != processor.sensitivity:
                processor.memory = memory
                processor.sensitivity = sensitivity
                processor.min_hits = int(1 + sensitivity * 4)
                processor.iou_threshold = 0.5 - (sensitivity * 0.4)
                processor.tracker = Sort(
                    max_age=memory,
                    min_hits=processor.min_hits,
                    iou_threshold=processor.iou_threshold,
                )
                print(f"Settings updated: memory={memory}, sensitivity={sensitivity}")
        except Exception as e:
            print(f"Error watching settings: {e}")
        time.sleep(3)


class LabelConverter:
    def __init__(self):
        self.converted_label_map = {
            1: 1,
            2: 2,
            3: 2,
            4: 2,
            6: 2,
            8: 2,
            18: 3,
            19: 3,
            20: 3,
            21: 3,
        }

    def convert_labels(self, labels: List[int]) -> List[int]:
        return [self.converted_label_map.get(label, label) for label in labels]


class DetectionProcessor:
    def __init__(
        self,
        redis_host: str,
        redis_port: int,
        input_queue: str,
        output_queue: str,
        sensitivity: float,
        memory: int,
    ):
        self.redis_client = RedisClient(host=redis_host, port=redis_port)
        self.label_converter = LabelConverter()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sensitivity = sensitivity
        self.memory = memory
        self.min_hits = int(1 + sensitivity * 4)
        self.iou_threshold = 0.5 - (sensitivity * 0.4)
        self.tracker = Sort(
            max_age=memory, min_hits=self.min_hits, iou_threshold=self.iou_threshold
        )

    def process_detections(self):
        while True:
            print("memory:", self.memory)
            print("sensitivity:", self.sensitivity)
            detection_bytes = self.redis_client.pop_from_queue(self.input_queue)

            if detection_bytes:
                detection = json.loads(detection_bytes[0])
                dets = np.array(
                    [
                        box + [score]
                        for box, score in zip(detection["boxes"], detection["scores"])
                    ]
                )

                converted_labels = self.label_converter.convert_labels(
                    detection["labels"]
                )
                detection_ids = self.tracker.update(dets=dets, labels=converted_labels)
                detection_ids_list = self.format_detection_ids(detection_ids)

                self.redis_client.push_to_queue(
                    self.output_queue, [json.dumps(detection_ids_list).encode()]
                )
            else:
                print("Queue is empty, waiting...")
                time.sleep(2)

    @staticmethod
    def format_detection_ids(detection_ids: np.ndarray) -> List[List[int]]:
        return [
            [
                int(value) if idx >= len(row) - 2 else value
                for idx, value in enumerate(row)
            ]
            for row in detection_ids.tolist()
        ]


notify.py:
import redis
import json
import uuid
import cv2
from datetime import datetime
from collections import Counter
from utils import draw_detection_with_det, decode_img
from db import add_notification

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
                _ = add_notification(frame_count, labels, unique_id, frame_time)

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


def add_notification(
    frame_count: int, labels: List[dict], image_url: str, frame_time: float
) -> str:
    record = Notification(
        frame_count=frame_count,
        labels=labels,
        image_url=image_url,
        time=datetime.fromtimestamp(frame_time),
    )

    insert_data = record.model_dump(by_alias=True, exclude={"id"})
    _ = notifications_collection.insert_one(insert_data)

    asyncio.run(publish_to_redis(insert_data))

    return insert_data


main.py:
from multiprocessing import Process
import threading
import frame_producer
import inference
import tracking
import notify
from  redis_client import RedisClient


def start_frame_producer():
    producer = frame_producer.FrameProducer(
        output_queue="frames_camera1", url_key="camera_url"
    )
    producer.capture_frames(encoding_method="binary")


def start_inference():
    redis_client = RedisClient(host="localhost", port=6379)
    frame_processor = inference.Inference(
        redis_client=redis_client,
        input_queue="frames_camera1",
        output_queue="detections",
        image_bytes_queue="image_bytes",
    )
    frame_processor.start()


def start_tracking():
    processor = tracking.DetectionProcessor(
        redis_host="localhost",
        redis_port=6379,
        input_queue="detections",
        output_queue="detection_ids",
        sensitivity=0.2,
        memory=5,
    )

    settings_thread = threading.Thread(
        target=tracking.watch_settings, args=(processor,), daemon=True
    )
    settings_thread.start()
    processor.process_detections()


def start_notification():
    notify.notify_objects(image_queue="image_bytes", detection_queue="detection_ids")


if __name__ == "__main__":
    processes = [
        Process(target=start_frame_producer),
        Process(target=start_tracking),
        Process(target=start_notification),
    ]

    threads = [
        threading.Thread(target=start_inference, daemon=True),
    ]

    for process in processes:
        process.start()

    for thread in threads:
        thread.start()

    for process in processes:
        process.join()

    for thread in threads:
        thread.join()
