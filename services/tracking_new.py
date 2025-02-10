import json
import numpy as np
import time
from typing import List
from sort import Sort
import redis
from threading import Thread


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
    # Tüm örnekler için ortak memory ve sensitivity
    memory = 5
    sensitivity = 0.2
    min_hits = int(1 + sensitivity * 4)
    iou_threshold = 0.5 - (sensitivity * 0.4)
    
    def __init__(self, redis_client, input_queue: str, output_queue: str):
        self.redis_client = redis_client
        self.label_converter = LabelConverter()
        self.input_queue = input_queue
        self.output_queue = output_queue

        # Tracker, sınıf değişkenlerinden başlatılıyor
        self.tracker = Sort(
            max_age=DetectionProcessor.memory, 
            min_hits=DetectionProcessor.min_hits, 
            iou_threshold=DetectionProcessor.iou_threshold
        )

    def process_detections(self):
        while True:
            detection_bytes = self.redis_client.rpop(self.input_queue)

            if detection_bytes:
                detection = json.loads(detection_bytes)
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

                self.redis_client.lpush(
                    self.output_queue, *[json.dumps(detection_ids_list).encode()]
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

    @classmethod
    def update_settings(cls, redis_client):
        """Tüm örnekler için memory ve sensitivity değerlerini günceller."""
        while True:
            try:
                memory = int(redis_client.get("tracking:memory") or cls.memory)
                sensitivity = float(redis_client.get("tracking:sensitivity") or cls.sensitivity)

                if memory != cls.memory or sensitivity != cls.sensitivity:
                    cls.memory = memory
                    cls.sensitivity = sensitivity
                    cls.min_hits = int(1 + sensitivity * 4)
                    cls.iou_threshold = 0.5 - (sensitivity * 0.4)

                    print(f"Global settings updated: memory={memory}, sensitivity={sensitivity}")
            except Exception as e:
                print(f"Error watching settings: {e}")

            time.sleep(3)


if __name__ == "__main__":
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=False)

    # Ayarları izlemek için tek bir thread başlatılır
    settings_thread = Thread(target=DetectionProcessor.update_settings, args=(redis_client,), daemon=True)
    settings_thread.start()

    # Birden fazla processor oluşturulabilir, ancak hepsi ortak ayarları kullanır
    processor1 = DetectionProcessor(
        redis_client=redis_client,
        input_queue="inference1",
        output_queue="tracking1",
    )

    processor2 = DetectionProcessor(
        redis_client=redis_client,
        input_queue="inference2",
        output_queue="tracking2",
    )

    # İşlem başlatılır
    processor1.process_detections()
