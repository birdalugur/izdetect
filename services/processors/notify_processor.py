import json
import uuid
import cv2
import os
import time
from datetime import datetime
from collections import Counter
from core.utils import draw_detection_with_det, decode_img
from core.base import Service
from core.interfaces import MessageBroker, DetectionRepository

class NotifyProcessor(Service):
    def __init__(
        self,
        repository: DetectionRepository,
        message_broker: MessageBroker,
        image_queue: str,
        detection_queue: str,
        camera_id: str,
        session_id: str,
    ):
        super().__init__(message_broker)
        self.repository = repository
        self.image_queue = image_queue
        self.detection_queue = detection_queue
        self.camera_id = camera_id
        self.session_id = session_id
        self.notified_object_ids = set()
        self.selected_label = {1, 2, 3, 4, 6, 8, 18, 19, 20, 21}
        self.stop_signal = False

        # Ensure data directory exists
        if not os.path.exists("data"):
            os.makedirs("data")

    def run(self):
        count = 0
        while not self.stop_signal:
            # Polling image queue
            image_bytes = self.message_broker.rpop(self.image_queue)
            if not image_bytes:
                time.sleep(0.01)
                continue

            # Polling detection queue with simple timeout logic
            detection_ids_bytes = None
            for _ in range(50): # ~5 seconds
                if self.stop_signal: break
                detection_ids_bytes = self.message_broker.rpop(self.detection_queue)
                if detection_ids_bytes:
                    break
                time.sleep(0.1)

            if not detection_ids_bytes:
                print("Warning: Timed out waiting for detection results matching image.")
                continue

            try:
                detection_ids = json.loads(detection_ids_bytes)

                filtered_detection_ids = [
                    det
                    for det in detection_ids
                    if det[-2] not in self.notified_object_ids
                    and det[-1] in self.selected_label
                ]

                if filtered_detection_ids:
                    image_array = decode_img(image_bytes)
                    for det in filtered_detection_ids:
                        det_id = det[-2]
                        if det_id not in self.notified_object_ids:
                            self.notified_object_ids.add(det_id)
                            draw_detection_with_det(image_array, det)

                    label_counts = Counter(det[-1] for det in filtered_detection_ids)
                    labels = [
                        {str(label_id): count}
                        for label_id, count in label_counts.items()
                    ]

                    unique_id = str(uuid.uuid4()) + ".jpg"
                    image_path = f"data/{unique_id}"
                    cv2.imwrite(image_path, image_array)

                    frame_time = datetime.now()

                    record = {
                        "frame_count": count,
                        "labels": labels,
                        "image_url": unique_id,
                        "time": frame_time,
                        "camera_id": self.camera_id,
                        "session_id": self.session_id,
                        "status": "active"
                    }

                    inserted_id = self.repository.add_notification(record)

                    # Add ID back to record for publishing if needed
                    record["id"] = inserted_id

                    # Convert datetime to string for JSON serialization
                    record["time"] = record["time"].isoformat()

                    self.message_broker.publish("event_channel", json.dumps(record))

            except Exception as e:
                print(f"Error in NotifyProcessor: {e}")

            count += 1

    def stop(self):
        self.stop_signal = True
