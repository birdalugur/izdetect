import json
import redis
import sort as sort_tracking
import numpy as np
import time

REDIS_HOST = "localhost"
REDIS_PORT = 6379
INPUT_QUEUE = "detections"
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

sensitivity = 0.2
memory = 5
min_hits = int(1 + sensitivity * 4)
iou_threshold = 0.5 - (sensitivity * 0.4)
sort_tracker = sort_tracking.Sort(
    max_age=memory, min_hits=min_hits, iou_threshold=iou_threshold
)

converted_label = {1: 1, 2: 2, 3: 2, 4: 2, 6: 2, 8: 2, 18: 3, 19: 3, 20: 3, 21: 3}


def process_dets():
    while True:
        detection_bytes = redis_client.rpop(INPUT_QUEUE)

        if detection_bytes:
            detection = json.loads(detection_bytes)
            dets = np.array(
                [
                    box + [score]
                    for box, score in zip(detection["boxes"], detection["scores"])
                ]
            )

            labels = np.array(detection["labels"])
            converted_labels = [converted_label.get(label, label) for label in labels]
            detection_ids = sort_tracker.update(dets=dets, labels=converted_labels)
            detection_ids_list = detection_ids.tolist()

            for row in detection_ids_list:
                row[-2] = int(row[-2])
                row[-1] = int(row[-1])

            detection_ids_json = json.dumps(detection_ids_list)
            redis_client.lpush("detection_ids", detection_ids_json)
        else:
            print("Kuyruk boş, bekleniyor...")
            time.sleep(2)


if __name__ == "__main__":
    process_dets()
