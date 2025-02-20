from runer import Runner
from frame_producer import FrameProducer
from inference import Inference
from tracking import DetectionProcessor
from notify import NotifyProcessor

if __name__ == "__main__":
    manager = Runner(mode="process")
    thread_runer = Runner(mode="thread")

    camera_urls = [
        "rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10",
        "rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10",
        "/home/birdal/izdetect/sahil.mp4",
        # "/home/birdal/izdetect/sahil.mp4"
    ]

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
        thread_runer.add_instance(inference)

    manager.start_all()
    thread_runer.start_all()
