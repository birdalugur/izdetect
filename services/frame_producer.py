import cv2
import redis
import time
from image_processor import ImageProcessor
from base import BaseClass


class FrameProducer(BaseClass):
    def __init__(
        self, video_source: str, output_queue: str, redis_client: redis.Redis = None
    ):
        self.video_source = video_source
        self.output_queue = output_queue
        super().__init__(redis_client)
        self.stop_signal = False

    def __repr__(self):
        return (
            f"FrameProducer(output_queue={self.output_queue}, "
            f"redis_client={self.redis_client}, "
            f"video_source={self.video_source})"
        )

    def run(self, encoding_method="binary"):
        cap = cv2.VideoCapture(self.video_source)
        if not cap.isOpened():
            print("Error opening video source.")
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
                    break
                else:
                    continue

            image_bytes = ImageProcessor.encode_img(
                frame, encoding_method=encoding_method
            )
            self.redis_client.lpush(self.output_queue, image_bytes)
            not_ret_count = 0

        cap.release()
        print("All frames processed. Waiting for a new camera URL...")


if __name__ == "__main__":
    processor = FrameProducer(
        output_queue="camera1", video_source="/home/birdal/izdetect/sahil.mp4"
    )
    processor.run(encoding_method="binary")

    # rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10
