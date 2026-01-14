import time
from typing import List, Optional
from core.base import Service
from core.interfaces import MessageBroker, ObjectDetector
from services.processors.image_processor import ImageProcessor

class Inference(Service):
    def __init__(
        self,
        detector: ObjectDetector,
        message_broker: MessageBroker,
        input_queue: str,
        output_queue: str,
        image_bytes_queue: str,
        batch_size: int = 5,
    ):
        super().__init__(message_broker)
        self.detector = detector
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.image_bytes_queue = image_bytes_queue
        self.batch_size = batch_size
        self.stop_signal = False

    def process_batch_frames(self, image_bytes_list: List[bytes]):
        if not image_bytes_list:
            return

        images = ImageProcessor.decode_image_batch(image_bytes_list)

        # Check if detector supports batching
        if hasattr(self.detector, 'detect_batch'):
            detection_results = self.detector.detect_batch(images)
        else:
            detection_results = [self.detector.detect(img) for img in images]

        serialized_results = ImageProcessor.serialize_detection_results(
            detection_results
        )

        if self.message_broker:
            if serialized_results:
                 for res in serialized_results:
                     self.message_broker.lpush(self.output_queue, res)

            for img_b in image_bytes_list:
                 self.message_broker.lpush(self.image_bytes_queue, img_b)

    def run(self):
        print("Inference Service Started.")
        while not self.stop_signal:
            batch = []
            # Try to fill the batch
            for _ in range(self.batch_size):
                # rpop from interface
                item = self.message_broker.rpop(self.input_queue)
                if item:
                    batch.append(item)
                else:
                    break

            if batch:
                try:
                    self.process_batch_frames(batch)
                except Exception as e:
                    print(f"Error in inference batch: {e}")
            else:
                time.sleep(0.01)

    def stop(self):
        self.stop_signal = True
        print("Inference Service Stopped.")
