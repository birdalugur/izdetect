import json
import numpy as np
import time
from typing import List
from core.sort import Sort
from core.base import Service
from core.interfaces import MessageBroker, DetectionRepository

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


class DetectionProcessor(Service):
    def __init__(self, repository: DetectionRepository, message_broker: MessageBroker, input_queue: str, output_queue: str):
        super().__init__(message_broker)
        self.repository = repository
        self.label_converter = LabelConverter()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stop_signal = False

        # Initial MongoDB config fetch
        try:
            config = self.repository.get_settings()
            self.memory = int(config.get("memory", 5))
            self.sensitivity = float(config.get("sensitivity", 0.2))
        except Exception as e:
            print(f"Error fetching settings: {e}. Using defaults.")
            self.memory = 5
            self.sensitivity = 0.2

        self.min_hits = int(1 + self.sensitivity * 4)
        self.iou_threshold = 0.5 - (self.sensitivity * 0.4)

        self.tracker = Sort(
            max_age=self.memory,
            min_hits=self.min_hits,
            iou_threshold=self.iou_threshold,
        )

    def run(self):
        while not self.stop_signal:
            detection_bytes = self.message_broker.rpop(self.input_queue)
            if detection_bytes:
                try:
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

                    msg = json.dumps(detection_ids_list)
                    self.message_broker.lpush(self.output_queue, msg)
                except Exception as e:
                    print(f"Error in DetectionProcessor: {e}")
            else:
                time.sleep(0.1)

    def stop(self):
        self.stop_signal = True

    @staticmethod
    def format_detection_ids(detection_ids: np.ndarray) -> List[List[int]]:
        return [
            [
                int(value) if idx >= len(row) - 2 else value
                for idx, value in enumerate(row)
            ]
            for row in detection_ids.tolist()
        ]
