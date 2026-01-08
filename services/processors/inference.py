import time
import sys
import os

# Ensure we can import modules from parent directories if needed,
# though ideally we fix the imports to be absolute or relative properly.
# Assuming services is a package.

import services.model as model
from typing import List
import redis
from services.processors.image_processor import ImageProcessor
from services.core.base import Service


class Inference(Service):
    def __init__(
        self,
        input_queue: str,
        output_queue: str,
        image_bytes_queue: str,
        batch_size: int = 5,
        redis_client: redis.Redis = None,
    ):
        super().__init__(redis_client)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.image_bytes_queue = image_bytes_queue
        self.batch_size = batch_size
        self.stop_signal = False

    def process_single_frame(self, image_bytes: bytes):
        image = ImageProcessor.decode_image(image_bytes)
        detections = model.process_frame(image)
        ImageProcessor.save_image_with_detections(image, detections)
        # Note: push_to_queue is not a standard redis method.
        # Assuming rpush or lpush was intended or it's a wrapper method I missed in base?
        # Checking base class... base class has standard redis client.
        # Assuming lpush for now as per other methods.
        self.redis_client.lpush(self.image_bytes_queue, image_bytes)

    def process_batch_frames(self, image_bytes_list: List[bytes]):
        images = ImageProcessor.decode_image_batch(image_bytes_list)
        detection_results = model.process_batch(images)
        serialized_results = ImageProcessor.serialize_detection_results(
            detection_results
        )
        if serialized_results:
             self.redis_client.lpush(self.output_queue, *serialized_results)
        if image_bytes_list:
             self.redis_client.lpush(self.image_bytes_queue, *image_bytes_list)

    def run(self):
        while not self.stop_signal:
            # redis rpop with count (batch_size) returns list or None
            # Standard redis-py rpop(name, count) returns list
            image_bytes = self.redis_client.rpop(self.input_queue, self.batch_size)
            if image_bytes:
                if isinstance(image_bytes, bytes):
                    self.process_single_frame(image_bytes)
                elif isinstance(image_bytes, list):
                    self.process_batch_frames(image_bytes)
            else:
                # print("Queue is empty, inference waiting...")
                time.sleep(0.1)

    def stop(self):
        self.stop_signal = True
