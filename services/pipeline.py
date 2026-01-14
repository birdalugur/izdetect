from typing import List, Optional

from core.service_runner import ServiceManager
from services.processors.frame_producer import FrameProducer
from services.processors.inference import Inference
from services.processors.detection_processor import DetectionProcessor
from services.processors.notify_processor import NotifyProcessor
from infrastructure.redis_broker import RedisBroker
from infrastructure.mongo_repository import MongoDetectionRepository
from infrastructure.opencv_source import OpenCVVideoSource
from core.interfaces import ObjectDetector

class CameraPipeline:
    def __init__(self, camera_url: str, camera_idx: int, runner_process: ServiceManager, runner_thread: ServiceManager):
        self.camera_url = camera_url
        self.camera_idx = camera_idx
        self.camera_id = f"cam-{camera_idx}"
        self.runner_process = runner_process
        self.runner_thread = runner_thread

        self.session_id: Optional[str] = None

        # Queues
        self.q_raw_frames = f"camera{camera_idx}"
        self.q_inference_out = f"inference{camera_idx}"
        self.q_inf_images = f"camera{camera_idx}_inf"
        self.q_tracking_out = f"tracking{camera_idx}"

        # Infrastructure
        self.broker = RedisBroker()
        self.repository = MongoDetectionRepository()

        # Components
        self.frame_producer: Optional[FrameProducer] = None
        self.inference: Optional[Inference] = None
        self.detection_processor: Optional[DetectionProcessor] = None
        self.notify_processor: Optional[NotifyProcessor] = None

    def start(self, detector: ObjectDetector):
        # 1. Start Session
        self.session_id = self.repository.add_detection_session(camera_id=self.camera_id)

        # 2. Initialize Components
        video_source = OpenCVVideoSource(self.camera_url)

        self.frame_producer = FrameProducer(
            video_source=video_source,
            message_broker=self.broker,
            output_queue=self.q_raw_frames,
            camera_id=self.camera_id
        )

        self.inference = Inference(
            detector=detector,
            message_broker=self.broker,
            input_queue=self.q_raw_frames,
            output_queue=self.q_inference_out,
            image_bytes_queue=self.q_inf_images,
        )

        self.detection_processor = DetectionProcessor(
            repository=self.repository,
            message_broker=self.broker,
            input_queue=self.q_inference_out,
            output_queue=self.q_tracking_out
        )

        self.notify_processor = NotifyProcessor(
            repository=self.repository,
            message_broker=self.broker,
            image_queue=self.q_inf_images,
            detection_queue=self.q_tracking_out,
            camera_id=self.camera_id,
            session_id=self.session_id,
        )

        # 3. Add to runners
        self.runner_process.add_instance(self.frame_producer)
        self.runner_process.add_instance(self.detection_processor)
        self.runner_process.add_instance(self.notify_processor)

        self.runner_thread.add_instance(self.inference)

        print(f"Pipeline initialized for {self.camera_id}")

    def stop(self):
        if self.session_id:
            self.repository.update_session_end(self.session_id)
            self.session_id = None
