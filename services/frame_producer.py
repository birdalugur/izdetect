import cv2
import redis
import time
from image_processor import ImageProcessor
from base import BaseClass


class FrameProducer(BaseClass):
    def __init__(
        self,
        video_source: str,
        output_queue: str,
        camera_id: str,
        redis_client: redis.Redis = None,
    ):
        self.video_source = video_source
        self.output_queue = output_queue
        self.camera_id = camera_id  # Yeni: Kamera kimliği
        self.is_connected = False  # Kamera bağlantı durumu
        super().__init__(redis_client)
        self.stop_signal = False

    def stop(self):
        """Kamera bağlantısını kes ve işlemi durdur."""
        self.stop_signal = True
        self.is_connected = False
        print(f"Stopping FrameProducer for camera {self.camera_id}...")

    def run(self, encoding_method="binary"):
        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            cap = cv2.VideoCapture(self.video_source)
            if not cap.isOpened():
                print(f"Error opening video source {self.video_source}. Retrying...")
                retry_count += 1
                time.sleep(2)
                continue
            else:
                self.is_connected = True
                break

        if not self.is_connected:
            print(
                f"Failed to connect to {self.video_source} after {max_retries} retries."
            )
            self.redis_client.publish("task_control", "disconnected")
            return

        not_ret_count = 0
        while not self.stop_signal:
            ret, frame = cap.read()
            if not ret:
                not_ret_count += 1
                print("No frames from camera, retrying {}...".format(not_ret_count))
                time.sleep(0.1)
                if not_ret_count > 5:
                    print("Camera disconnected, switching to URL wait mode.")
                    self.stop_signal = True
                    self.redis_client.publish("task_control", "disconnected")
                    break
                else:
                    continue

            image_bytes = ImageProcessor.encode_img(
                frame, encoding_method=encoding_method
            )
            self.redis_client.lpush(self.output_queue, image_bytes)
            not_ret_count = 0

        cap.release()


if __name__ == "__main__":
    processor = FrameProducer(
        output_queue="camera1",
        video_source="/home/birdal/izdetect/sahil.mp4",
        camera_id="deneme",
    )
    processor.run(encoding_method="binary")
