import cv2
import redis
import time
import os
from processors.image_processor import ImageProcessor
from core.base import Service


class FrameProducer(Service):
    def __init__(
        self,
        video_source: str,
        output_queue: str,
        camera_id: str,
        redis_client: redis.Redis = None,
    ):
        super().__init__(redis_client)
        self.video_source = video_source
        self.output_queue = output_queue
        self.camera_id = camera_id
        self.is_connected = False
        self.stop_signal = False

    def stop(self):
        """Kamera bağlantısını kes ve işlemi durdur."""
        self.stop_signal = True
        self.is_connected = False
        print(f"Stopping FrameProducer for camera {self.camera_id}...")

    def run(self, encoding_method="binary"):
        # Set timeout to 5000ms (5 seconds) to avoid long hangs on connection loss
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "timeout;5000"

        print(f"[{self.camera_id}] FrameProducer started for {self.video_source}")

        # Outer loop handles connection/reconnection
        while not self.stop_signal:
            cap = cv2.VideoCapture(self.video_source)
            if not cap.isOpened():
                print(f"[{self.camera_id}] Error opening video source. Retrying in 2s...")
                time.sleep(2)
                continue

            self.is_connected = True
            print(f"[{self.camera_id}] Connected to {self.video_source}")

            not_ret_count = 0

            # Inner loop handles frame reading
            while not self.stop_signal:
                ret, frame = cap.read()
                if not ret:
                    not_ret_count += 1
                    # Log every 10 failures to avoid spamming
                    if not_ret_count % 10 == 0:
                        print(f"[{self.camera_id}] No frames, retrying {not_ret_count}...")

                    # If we fail enough times, assume connection lost
                    if not_ret_count > 5:
                        print(f"[{self.camera_id}] Connection lost. Reconnecting...")
                        break

                    time.sleep(0.1)
                    continue

                # Reset failure counter on success
                not_ret_count = 0

                try:
                    image_bytes = ImageProcessor.encode_img(
                        frame, encoding_method=encoding_method
                    )
                    if self.redis_client:
                        self.redis_client.lpush(self.output_queue, image_bytes)
                except Exception as e:
                    print(f"[{self.camera_id}] Error processing frame: {e}")

            cap.release()
            self.is_connected = False

            # If stopped, we exit outer loop.
            # If not stopped (meaning connection lost), wait a bit before reconnecting.
            if not self.stop_signal:
                time.sleep(1)

        print(f"[{self.camera_id}] FrameProducer stopped.")
