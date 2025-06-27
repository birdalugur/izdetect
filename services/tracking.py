import json
import numpy as np
import time
from typing import List
from threading import Thread
from sort import Sort
from base import BaseClass
from db import get_settings  # import MongoDB-based settings function


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

        # Initial MongoDB config fetch
        config = get_settings()
        self.memory = int(config.get("memory", 5))
        self.sensitivity = float(config.get("sensitivity", 0.2))
        self.min_hits = int(1 + self.sensitivity * 4)
        self.iou_threshold = 0.5 - (self.sensitivity * 0.4)

        self.tracker = Sort(
            max_age=self.memory,
            min_hits=self.min_hits,
            iou_threshold=self.iou_threshold,
        )

    def run(self):
        while True:
            detection_bytes = self.redis_client.rpop(
                self.input_queue
            )  # You may keep Redis for queuing
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
                print("Queue is empty, Tracking waiting...")
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


if __name__ == "__main__":
    processor = DetectionProcessor(input_queue="inference1", output_queue="tracking1")
    processor.run()
