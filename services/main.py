from runer import Runner
from frame_producer import FrameProducer
from inference import Inference
from tracking import DetectionProcessor
from notify import NotifyProcessor
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


if __name__ == "__main__":
    manager1 = Runner(mode='process')
    thread_runer = Runner(mode='thread')

    task1 = FrameProducer(
        video_source="rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10",
        output_queue="camera1",
    )
    task2 = FrameProducer(
        video_source="rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10",
        output_queue="camera2",
    )

    task3 = Inference(
        input_queue="camera1",
        output_queue="inference1",
        image_bytes_queue="camera1_inf",
    )
    task4 = Inference(
        input_queue="camera2",
        output_queue="inference2",
        image_bytes_queue="camera2_inf",
    )

    task5 = DetectionProcessor(input_queue="inference1", output_queue="tracking1")
    task6 = DetectionProcessor(input_queue="inference2", output_queue="tracking2")

    task7 = NotifyProcessor(
        image_queue="camera1_inf", detection_queue="tracking1", camera_id=1
    )
    task8 = NotifyProcessor(
        image_queue="camera2_inf", detection_queue="tracking2", camera_id=2
    )

    manager1.add_instance(task1)
    manager1.add_instance(task2)
    manager1.add_instance(task5)
    manager1.add_instance(task6)
    manager1.add_instance(task7)
    manager1.add_instance(task8)

    thread_runer.add_instance(task3)
    thread_runer.add_instance(task4)

    manager1.start_all()
    thread_runer.start_all()
