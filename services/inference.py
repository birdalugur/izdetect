import time
import model
from typing import List
import redis
from image_processor import ImageProcessor
from base import BaseClass


class Inference(BaseClass):
    def __init__(
        self,
        input_queue: str,
        output_queue: str,
        image_bytes_queue: str,
        redis_client: redis.Redis = None,
    ):
        super().__init__(redis_client)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.image_bytes_queue = image_bytes_queue
        self.idle_count = 0

    def process_single_frame(self, image_bytes: bytes):
        """Processes a single image frame."""
        image = ImageProcessor.decode_image(image_bytes)
        detections = model.process_frame(image)
        ImageProcessor.save_image_with_detections(image, detections)
        self.redis_client.push_to_queue(self.image_bytes_queue, [image_bytes])

    def process_batch_frames(self, image_bytes_list: List[bytes]):
        """Processes a batch of image frames."""
        images = ImageProcessor.decode_image_batch(image_bytes_list)
        detection_results = model.process_batch(images)
        serialized_results = ImageProcessor.serialize_detection_results(
            detection_results
        )
        self.redis_client.lpush(self.output_queue, *serialized_results)
        self.redis_client.lpush(self.image_bytes_queue, *image_bytes_list)

    def run(self):
        """Main loop to process frames from the Redis queue."""
        while True:
            image_bytes = self.redis_client.rpop(self.input_queue, 5)

            if image_bytes:
                self.idle_count = 0
                if isinstance(image_bytes, bytes):
                    self.process_single_frame(image_bytes)
                elif isinstance(image_bytes, list):
                    self.process_batch_frames(image_bytes)
            else:
                self.idle_count += 1
                print("Queue is empty, waiting...")
                time.sleep(1)

                if self.idle_count >= 5:
                    print("Queue is empty, entering sleep mode.")
                    time.sleep(5)


if __name__ == "__main__":
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=False)
    inference = Inference(
        input_queue="camera1",
        output_queue="inference1",
        image_bytes_queue="camera1_image_bytes"
    )
    inference.run()
