import uuid
import time
import numpy as np
import cv2
import model
import utils
import json
from typing import List, Dict
from redis_client import RedisClient


class ImageProcessor:
    @staticmethod
    def decode_image(image_bytes: bytes) -> np.ndarray:
        """Decodes a single image from bytes."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    @staticmethod
    def decode_image_batch(image_bytes_list: List[bytes]) -> List[np.ndarray]:
        """Decodes a batch of images."""
        return [
            ImageProcessor.decode_image(image_bytes) for image_bytes in image_bytes_list
        ]

    @staticmethod
    def serialize_detection_results(results: List[Dict[str, any]]) -> List[str]:
        """Serializes detection results for Redis storage."""
        serialized_results = []
        for result in results:
            serialized_result = {
                "scores": result["scores"].cpu().tolist(),
                "labels": result["labels"].cpu().tolist(),
                "boxes": result["boxes"].cpu().tolist(),
            }
            serialized_results.append(json.dumps(serialized_result))
        return serialized_results

    @staticmethod
    def save_image_with_detections(
        image: np.ndarray, detections: Dict[str, any], output_dir: str = "output"
    ) -> str:
        """Draws detections on the image and saves it."""
        image_with_detections = utils.draw_detections(image, detections)
        unique_id = str(uuid.uuid4())
        output_path = f"{output_dir}/{unique_id}.jpg"
        cv2.imwrite(output_path, image_with_detections)
        return output_path


class FrameProcessor:
    def __init__(
        self,
        redis_client: RedisClient,
        input_queue: str,
        output_queue: str,
        image_bytes_queue: str,
    ):
        self.redis_client = redis_client
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
        self.redis_client.push_to_queue(self.output_queue, serialized_results)
        self.redis_client.push_to_queue(self.image_bytes_queue, image_bytes_list)

    def process_frames(self):
        """Main loop to process frames from the Redis queue."""
        while True:
            image_bytes = self.redis_client.pop_from_queue(self.input_queue, 5)

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
    redis_client = RedisClient(host="localhost", port=6379)
    frame_processor = FrameProcessor(
        redis_client=redis_client,
        input_queue="frames_camera1",
        output_queue="detections",
        image_bytes_queue="image_bytes",
    )
    frame_processor.process_frames()

    # frame_packet = pickle.loads(frame_data[1])
    # frame_number = frame_packet["frame_number"]
    # frame = np.frombuffer(frame_packet["frame_data"], dtype=np.uint8)
    # frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
