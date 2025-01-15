from multiprocessing import Process
import threading
import frame_producer
import inference
import tracking
import notify
from redis_client import RedisClient

def start_frame_producer(output_queue, url_key):
    producer = frame_producer.FrameProducer(
        output_queue=output_queue, url_key=url_key
    )
    producer.capture_frames(encoding_method="binary")

def start_inference(input_queue, output_queue, image_bytes_queue):
    redis_client = RedisClient(host="localhost", port=6379)
    frame_processor = inference.Inference(
        redis_client=redis_client,
        input_queue=input_queue,
        output_queue=output_queue,
        image_bytes_queue=image_bytes_queue,
    )
    frame_processor.start()

def start_tracking(input_queue, output_queue, camera_id):
    processor = tracking.DetectionProcessor(
        redis_host="localhost",
        redis_port=6379,
        input_queue=input_queue,
        output_queue=output_queue,
        sensitivity=0.2,
        memory=5,
    )

    settings_thread = threading.Thread(
        target=tracking.watch_settings, args=(processor,), daemon=True
    )
    settings_thread.start()
    processor.process_detections()

def start_notification(image_queue, detection_queue, camera_id):
    notify.notify_objects(image_queue=image_queue, detection_queue=detection_queue, camera_id=camera_id)

if __name__ == "__main__":
    # Kamera kaynaklarını ve kuyruk yapılarını tanımlayın
    cameras = [
        {"id": 1, "url_key": "camera_url", "queues": {
            "frames": "frames_camera1",
            "detections": "detections_camera1",
            "image_bytes": "image_bytes_camera1",
            "detection_ids": "detection_ids_camera1"
        }},
        {"id": 2, "url_key": "camera2_url", "queues": {
            "frames": "frames_camera2",
            "detections": "detections_camera2",
            "image_bytes": "image_bytes_camera2",
            "detection_ids": "detection_ids_camera2"
        }}
    ]

    processes = []
    threads = []

    for camera in cameras:
        # Her kamera için frame producer süreci
        processes.append(
            Process(
                target=start_frame_producer,
                args=(camera["queues"]["frames"], camera["url_key"]),
            )
        )

        # Her kamera için inference iş parçacığı
        threads.append(
            threading.Thread(
                target=start_inference,
                args=(
                    camera["queues"]["frames"],
                    camera["queues"]["detections"],
                    camera["queues"]["image_bytes"],
                ),
                daemon=True,
            )
        )

        # Her kamera için tracking süreci
        processes.append(
            Process(
                target=start_tracking,
                args=(
                    camera["queues"]["detections"],
                    camera["queues"]["detection_ids"],
                    camera["id"],
                ),
            )
        )

        # Her kamera için bildirim süreci
        processes.append(
            Process(
                target=start_notification,
                args=(
                    camera["queues"]["image_bytes"],
                    camera["queues"]["detection_ids"],
                    camera["id"],
                ),
            )
        )

    # Tüm süreçleri başlat
    for process in processes:
        process.start()

    # Tüm iş parçacıklarını başlat
    for thread in threads:
        thread.start()

    # Süreçlerin tamamlanmasını bekle
    for process in processes:
        process.join()

    # İş parçacıklarının tamamlanmasını bekle
    for thread in threads:
        thread.join()
