import uuid
import redis
import time
import numpy as np
import cv2
import model
import utils
import json

# from processing_timer import ProcessingTimer

REDIS_HOST = "localhost"
REDIS_PORT = 6379
FRAME_QUEUE = "video_frames"
NOTIFICATION_QUEUE = "notification_queue"
# timer = ProcessingTimer()


def decode_img(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def decode_img_list(image_bytes: list) -> list:
    return [decode_img(image_byte) for image_byte in image_bytes]


def serialize_results(results):
    serialized_results = []
    for result in results:
        serialized_result = {
            "scores": result["scores"].cpu().tolist(),
            "labels": result["labels"].cpu().tolist(),
            "boxes": result["boxes"].cpu().tolist(),
        }
        serialized_results.append(json.dumps(serialized_result))
    return serialized_results


def process_frames():
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    idle_count = 0
    count = 0
    while True:
        count += 1
        image_bytes = redis_client.rpop(FRAME_QUEUE, 5)
        if image_bytes:
            idle_count = 0

            if isinstance(image_bytes, bytes):
                img = decode_img(image_bytes)
                result = model.process_frame(img)
                img_dets = utils.draw_detections(img, result)
                unique_id = str(uuid.uuid4())
                cv2.imwrite(f"output/{unique_id}.jpg", img_dets)

            elif isinstance(image_bytes, list):
                imgs = decode_img_list(image_bytes)
                results = model.process_batch(imgs)
                redis_client.lpush("image_bytes", *image_bytes)
                serialized_results = serialize_results(results)
                redis_client.lpush("detections", *serialized_results)

            print("Frame işlendi.")

        else:
            # timer.print_summary()
            idle_count += 1
            print("Kuyruk boş, bekleniyor...")
            time.sleep(1)

            if idle_count >= 5:
                print("Kuyruk boş, uyku moduna geçiliyor.")
                time.sleep(5)


if __name__ == "__main__":
    process_frames()

    # frame_packet = pickle.loads(frame_data[1])
    # frame_number = frame_packet["frame_number"]
    # frame = np.frombuffer(frame_packet["frame_data"], dtype=np.uint8)
    # frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
