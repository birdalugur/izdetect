import redis
from runer import Runner
from frame_producer import FrameProducer
from inference import Inference
from tracking import DetectionProcessor
from notify import NotifyProcessor
from multiprocessing import Event
import os
import time
from db import add_detection_session, update_detection_session_end, get_db

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Dictionary to store session_ids for each camera
camera_sessions = {}

db, _ = get_db()


def fetch_camera_urls():
    camera_collection = db["cameras"]
    return [cam["ip"] for cam in camera_collection.find()]


def start_tasks():
    global running, camera_urls, camera_sessions

    if running.is_set():
        print("Tasks are already running.")
        return

    camera_urls = fetch_camera_urls()
    print(f"Updated camera URLs: {camera_urls}")

    running.set()
    camera_sessions.clear()

    for idx, url in enumerate(camera_urls, start=1):
        camera_id = f"cam-{idx}"
        # Generate a new session_id for this camera
        session_id = add_detection_session(camera_id=camera_id)
        camera_sessions[camera_id] = session_id
        # Add session to database

        frame_producer = FrameProducer(
            video_source=url, output_queue=f"camera{idx}", camera_id=camera_id
        )
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
            camera_id=camera_id,  # Use camera_id as string
            session_id=session_id,
        )

        manager.add_instance(frame_producer)
        manager.add_instance(detection_processor)
        manager.add_instance(notify_processor)
        thread_runner.add_instance(inference)

    manager.start_all()
    thread_runner.start_all()


def stop_tasks():
    global running, camera_sessions
    if not running.is_set():
        print("No tasks are running.")
        return

    running.clear()
    # Update end time for each session
    for camera_id, session_id in camera_sessions.items():
        update_detection_session_end(session_id)
    camera_sessions.clear()
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
            print(f"Received command: {command}")
            if command == "start":
                start_tasks()
            elif command == "stop":
                print("Stop command received. Stopping tasks...")
                stop_tasks()
            elif command == "disconnected":
                print(
                    "Camera disconnected signal received. Restarting tasks after 8 seconds..."
                )
                time.sleep(6)
                stop_tasks()
                time.sleep(3)
                start_tasks()


if __name__ == "__main__":
    manager = Runner(mode="process")
    thread_runner = Runner(mode="thread")
    running = Event()

    redis_listener()
