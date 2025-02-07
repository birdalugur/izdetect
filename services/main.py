from multiprocessing import Process
import threading
import frame_producer
import inference
import tracking
import notify
from redis_client import redis_client
import json



def get_cameras():
    """Redis'ten kamera URL listesini çeker."""
    try:
        camera_urls = redis_client.get("camera_urls")
        if not camera_urls:
            return []

        camera_urls = json.loads(camera_urls)
        cameras = []

        for idx, url in enumerate(camera_urls):
            cameras.append(
                {
                    "id": idx + 1,
                    "url_key": url,
                    "queues": {
                        "frames": f"frames_camera_{idx+1}",
                        "detections": f"detections_camera_{idx+1}",
                        "image_bytes": f"image_bytes_camera_{idx+1}",
                        "detection_ids": f"detection_ids_camera_{idx+1}",
                    },
                }
            )

        return cameras
    except Exception as e:
        print(f"Redis'ten kameraları alırken hata: {e}")
        return []


def start_frame_producer(output_queue, rtsp_url):
    producer = frame_producer.FrameProducer(
        redis_client=redis_client, output_queue=output_queue, url_key=rtsp_url
    )
    producer.run(encoding_method="binary")


def start_inference(input_queue, output_queue, image_bytes_queue):
    frame_processor = inference.Inference(
        redis_client=redis_client,
        input_queue=input_queue,
        output_queue=output_queue,
        image_bytes_queue=image_bytes_queue,
    )
    frame_processor.start()


def start_tracking(input_queue, output_queue, camera_id):
    processor = tracking.DetectionProcessor(
        redis_client=redis_client,
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
    """Bildirim gönderme işlemini başlatır."""
    notify.notify_objects(
        image_queue=image_queue, detection_queue=detection_queue, camera_id=camera_id
    )


if __name__ == "__main__":
    cameras = get_cameras()
    if not cameras:
        print("Hata: Redis'te kamera bilgisi bulunamadı!")
        exit(1)

    processes = []
    threads = []

    for camera in cameras:
        processes.append(
            Process(
                target=start_frame_producer,
                args=(camera["queues"]["frames"], camera["url_key"]),
            )
        )

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

    for process in processes:
        process.start()

    for thread in threads:
        thread.start()

    for process in processes:
        process.join()

    for thread in threads:
        thread.join()
