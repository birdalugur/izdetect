from multiprocessing import Process
import threading
import frame_producer
import inference
import tracking
import notify


def start_frame_producer():
    producer = frame_producer.FrameProcessor(
        output_queue="frames_camera1", url_key="camera_url"
    )
    producer.capture_frames(encoding_method="binary")


def start_frame_consumer():
    redis_client = inference.RedisClient(host="localhost", port=6379)
    frame_processor = inference.FrameProcessor(
        redis_client=redis_client,
        input_queue="frames_camera1",
        output_queue="detections",
        image_bytes_queue="image_bytes",
    )
    frame_processor.process_frames()


def start_tracking():
    processor = tracking.DetectionProcessor(
        redis_host="localhost",
        redis_port=6379,
        input_queue="detections",
        output_queue="detection_ids",
        sensitivity=0.2,
        memory=5,
    )

    settings_thread = threading.Thread(
        target=tracking.watch_settings, args=(processor,), daemon=True
    )
    settings_thread.start()
    processor.process_detections()
    processor.process_detections()


def start_notification():
    notify.notify_objects(image_queue="image_bytes", detection_queue="detection_ids")


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
