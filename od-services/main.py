from multiprocessing import Process
import frame_producer
import inference
import tracking
import notify

import torch.multiprocessing as mp


def start_frame_producer():
    producer = frame_producer.FrameProcessor()
    producer.capture_frames(encoding_method="binary")


def start_frame_consumer():
    inference.process_frames()


def start_tracking():
    tracking.process_dets()


def start_notification():
    notify.notify_objects()


if __name__ == "__main__":
    mp.set_start_method("spawn")
    processes = [
        Process(target=start_frame_producer),
        mp.Process(target=start_frame_consumer, daemon=True),
        Process(target=start_tracking),
        Process(target=start_notification),
    ]

    for process in processes:
        process.start()

    for process in processes:
        process.join()
