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


if __name__ == "__main__":
    notify_objects(image_queue="image_bytes", detection_queue="detection_ids")
