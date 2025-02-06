import json
import numpy as np
import time
from typing import List
from sort import Sort


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
        redis_client,
        input_queue: str,
        output_queue: str,
        sensitivity: float,
        memory: int,
    ):
        self.redis_client = (redis_client,)
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


if __name__ == "__main__":
    processor = DetectionProcessor(
        redis_host="localhost",
        redis_port=6379,
        input_queue="detections",
        output_queue="detection_ids",
        sensitivity=0.2,
        memory=5,
    )

    from threading import Thread

    settings_thread = Thread(target=watch_settings, args=(processor,), daemon=True)
    settings_thread.start()
    processor.process_detections()
