import json
import numpy as np
import time
from typing import List
from threading import Thread
import redis
from sort import Sort
from base import BaseClass


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


class DetectionProcessor(BaseClass):
    def __init__(self, input_queue: str, output_queue: str, redis_client=None):
        super().__init__()
        self.redis_client = redis_client or self.redis_client
        self.label_converter = LabelConverter()
        self.input_queue = input_queue
        self.output_queue = output_queue

        # Başlangıç değerlerini Redis'ten al
        self.memory = int(self.redis_client.get("tracking:memory"))
        self.sensitivity = float(self.redis_client.get("tracking:sensitivity"))
        self.min_hits = int(1 + self.sensitivity * 4)
        self.iou_threshold = 0.5 - (self.sensitivity * 0.4)

        self.tracker = Sort(
            max_age=self.memory,
            min_hits=self.min_hits,
            iou_threshold=self.iou_threshold,
        )

        # Ayarları güncelleyen thread başlat
        self.settings_thread = Thread(target=self.update_settings, daemon=True)
        self.settings_thread.start()

    def run(self):
        while True:
            time.sleep(2)
            detection_bytes = self.redis_client.rpop(self.input_queue)
            if detection_bytes:
                print("memory: ", self.memory)
                print("sensitivity: ", self.sensitivity)
                self.redis_client.lpush(self.output_queue, detection_bytes)
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

    def update_settings(self):
        """Her instance kendi memory ve sensitivity değerlerini günceller."""
        while True:
            try:
                memory = int(self.redis_client.get("tracking:memory") or self.memory)
                sensitivity = float(
                    self.redis_client.get("tracking:sensitivity") or self.sensitivity
                )

                if memory != self.memory or sensitivity != self.sensitivity:
                    self.memory = memory
                    self.sensitivity = sensitivity
                    self.min_hits = int(1 + sensitivity * 4)
                    self.iou_threshold = 0.5 - (sensitivity * 0.4)

                    # Tracker'ı güncelle
                    self.tracker = Sort(
                        max_age=self.memory,
                        min_hits=self.min_hits,
                        iou_threshold=self.iou_threshold,
                    )

                    print(
                        f"[{self.input_queue}] Settings updated: memory={memory}, sensitivity={sensitivity}"
                    )
            except Exception as e:
                print(f"Error updating settings: {e}")

            time.sleep(3)


if __name__ == "__main__":
    processor1 = DetectionProcessor(
        input_queue="inference1",
        output_queue="inference1",
    )

    processor2 = DetectionProcessor(
        input_queue="inference2",
        output_queue="inference2",
    )

    # processor1.run()

    from runer import ParallelRunner

    manager = ParallelRunner()
    manager.add_instance(processor1)
    manager.add_instance(processor2)
    manager.start_all()
