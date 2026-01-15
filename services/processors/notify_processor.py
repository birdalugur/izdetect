import redis
import json
import uuid
import cv2
import os
from datetime import datetime
from collections import Counter
from core.utils import draw_detection_with_det, decode_img
from core.db import Record, add_notification
from core.base import Service

class NotifyProcessor(Service):
    def __init__(
        self,
        image_queue: str,
        detection_queue: str,
        camera_id: str,
        session_id: str,
        redis_client: redis.Redis=None,
    ):
        super().__init__(redis_client)
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
            # brpop blocks, so we need a timeout to check for stop signal
            # Using timeout=1 second
            res1 = self.redis_client.brpop(self.image_queue, timeout=1)
            if not res1:
                continue

            _, image_bytes = res1

            # We need to sync with detection queue.
            # This logic assumes strict 1:1 mapping and order which might be fragile but keeping as is for now.
            res2 = self.redis_client.brpop(self.detection_queue, timeout=5)
            if not res2:
                print("Warning: Timed out waiting for detection results matching image.")
                continue

            _, detection_ids_bytes = res2

            if image_bytes and detection_ids_bytes:
                try:
                    detection_ids = json.loads(detection_ids_bytes)

                    # Filter detections based on notified_object_ids and selected_label
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
                            else:
                                continue

                        label_counts = Counter(det[-1] for det in filtered_detection_ids)
                        labels = [
                            {str(label_id): count}
                            for label_id, count in label_counts.items()
                        ]

                        unique_id = str(uuid.uuid4()) + ".jpg"
                        image_path = f"data/{unique_id}"
                        cv2.imwrite(image_path, image_array)

                        # Use frame count and timestamp for notifications
                        frame_count = count
                        frame_time = datetime.now().isoformat()

                        record = Record(
                            frame_count=frame_count,
                            labels=labels,
                            image_url=unique_id,
                            time=frame_time,
                            camera_id=self.camera_id,
                            session_id=self.session_id,
                        )
                        inserted_data = add_notification(record=record)
                        self.publish_to_redis(inserted_data)
                except Exception as e:
                    print(f"Error in NotifyProcessor: {e}")

                count += 1

    def stop(self):
        self.stop_signal = True

    def publish_to_redis(self, data):
        try:
            message = json.dumps(data, default=str)
            self.redis_client.publish("event_channel", message)
        except Exception as e:
            print(f"Error publishing to Redis: {e}")
