from multiprocessing import Process
import threading
import frame_producer
import inference
import tracking
import notify


def start_frame_producer():
    producer = frame_producer.FrameProcessor(output_queue="frames_camera1", url_key="camera_url")
    producer.capture_frames(encoding_method="binary")


def start_frame_consumer():
    inference.process_frames()


def start_tracking():
    tracking.process_dets()


def start_notification():
    notify.notify_objects()


if __name__ == "__main__":
    processes = [
        Process(target=start_frame_producer),
        Process(target=start_tracking),
        Process(target=start_notification),
    ]

    threads = [
        threading.Thread(target=start_frame_consumer, daemon=True),
    ]

    for process in processes:
        process.start()

    for thread in threads:
        thread.start()

    for process in processes:
        process.join()

    for thread in threads:
        thread.join()
