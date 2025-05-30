import redis
from runer import Runner
from frame_producer import FrameProducer
from inference import Inference
from tracking import DetectionProcessor
from notify import NotifyProcessor
from multiprocessing import Event
import os
import time

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def fetch_camera_urls():
    return redis_client.lrange("camera_urls", 0, -1)


def start_tasks():
    global running, camera_urls

    if running.is_set():
        print("Tasks are already running.")
        return

    camera_urls = fetch_camera_urls()
    print(f"Updated camera URLs: {camera_urls}")

    running.set()

    for idx, url in enumerate(camera_urls, start=1):
        frame_producer = FrameProducer(video_source=url, output_queue=f"camera{idx}")
        inference = Inference(
            input_queue=f"camera{idx}",
            output_queue=f"inference{idx}",
            image_bytes_queue=f"camera{idx}_inf",
        )
        detection_processor = DetectionProcessor(
            input_queue=f"inference{idx}", output_queue=f"tracking{idx}"
        )
        notify_processor = NotifyProcessor(
            image_queue=f"camera{idx}_inf",
            detection_queue=f"tracking{idx}",
            camera_id=idx,
        )

        manager.add_instance(frame_producer)
        manager.add_instance(detection_processor)
        manager.add_instance(notify_processor)
        thread_runner.add_instance(inference)

    manager.start_all()
    thread_runner.start_all()


def stop_tasks():
    global running
    if not running.is_set():
        print("No tasks are running.")
        return

    running.clear()
    manager.stop_all()
    thread_runner.stop_all()
    redis_client.flushall()
    print("All tasks stopped. Waiting for start command.")


def redis_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("task_control")

    for message in pubsub.listen():
        if message["type"] == "message":
            command = message["data"].strip().lower()
            if command == "start":
                start_tasks()
            elif command == "stop":
                stop_tasks()
            elif command == "disconnected":
                print("Camera disconnected signal received. Restarting tasks after 8 seconds...")
                time.sleep(8)
                stop_tasks()


if __name__ == "__main__":
    manager = Runner(mode="process")
    thread_runner = Runner(mode="thread")
    running = Event()

    redis_listener()
