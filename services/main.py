import time
import sys
from multiprocessing import Event
from typing import Dict

from core.service_runner import ServiceManager
from infrastructure.redis_broker import RedisBroker
from infrastructure.mongo_repository import MongoDetectionRepository
from infrastructure.detr_detector import DetrObjectDetector
from services.pipeline import CameraPipeline

# Global State
running = Event()
pipelines: Dict[str, CameraPipeline] = {}
broker = RedisBroker()
repository = MongoDetectionRepository()

# Runners
process_runner = ServiceManager(mode="process")
thread_runner = ServiceManager(mode="thread")

detector = None

def fetch_camera_urls():
    return repository.get_camera_urls()

def start_tasks():
    global running, pipelines, detector

    if running.is_set():
        print("Tasks are already running.")
        return

    if detector is None:
        detector = DetrObjectDetector()

    camera_urls = fetch_camera_urls()
    print(f"Updated camera URLs: {camera_urls}")

    running.set()
    pipelines.clear()

    # Clear runners just in case
    process_runner.instances.clear()
    thread_runner.instances.clear()

    for idx, url in enumerate(camera_urls, start=1):
        camera_id = f"cam-{idx}"
        pipeline = CameraPipeline(
            camera_url=url,
            camera_idx=idx,
            runner_process=process_runner,
            runner_thread=thread_runner
        )
        pipeline.start(detector=detector)
        pipelines[camera_id] = pipeline

    process_runner.start_all()
    thread_runner.start_all()


def stop_tasks():
    global running, pipelines
    if not running.is_set():
        print("No tasks are running.")
        return

    running.clear()

    for pipeline in pipelines.values():
        pipeline.stop()

    pipelines.clear()

    process_runner.stop_all()
    thread_runner.stop_all()

    broker.flush_all()
    print("All tasks stopped. Waiting for start command.")


def redis_listener():
    pubsub = broker.subscribe("task_control")
    print("Redis listener started. Waiting for commands...")

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
    try:
        redis_listener()
    except KeyboardInterrupt:
        stop_tasks()
        print("Exiting...")
