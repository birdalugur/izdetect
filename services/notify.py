import redis
import json
import uuid
import cv2
from datetime import datetime
from collections import Counter
from utils import draw_detection_with_det, decode_img
from db import Record, add_notification
from redis_client import publish_to_redis
from base import BaseClass


class NotifyProcessor(BaseClass):
    def __init__(
        self,
        image_queue: str,
        detection_queue: str,
        camera_id: int,
        redis_client: redis.Redis=None,
    ):
        self.image_queue = image_queue
        self.detection_queue = detection_queue
        self.camera_id = camera_id
        super().__init__(redis_client)
        self.notified_object_ids = set()
        self.selected_label = {1, 2, 3, 4, 6, 8, 18, 19, 20, 21}

    def run(self):
        count = 0
        while True:
            _, image_bytes = self.redis_client.brpop(self.image_queue, timeout=0)
            _, detection_ids_bytes = self.redis_client.brpop(
                self.detection_queue, timeout=0
            )

            if image_bytes and detection_ids_bytes:
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
                    frame_time = datetime.timestamp(datetime.now())

                    record = Record(
                        frame_count=frame_count,
                        labels=labels,
                        image_url=unique_id,
                        time=frame_time,
                        camera_id=self.camera_id,
                    )
                    inserted_data = add_notification(record=record)
                    publish_to_redis(inserted_data)
                count += 1

if __name__ == "__main__":    
    task1 = NotifyProcessor(image_queue="camera1_inf", detection_queue="tracking1", camera_id=1)
    task1.run()
    