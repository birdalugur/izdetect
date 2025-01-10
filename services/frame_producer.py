import cv2
import redis
import time
import numpy as np
from processing_timer import ProcessingTimer
import base64


class FrameProcessor:
    def __init__(self, output_queue, url_key, redis_host="localhost", redis_port=6379):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.output_queue = output_queue
        self.url_key = url_key
        self.redis_client = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, decode_responses=True
        )
        self.video_source = None
        self.timer = ProcessingTimer()

    def get_camera_url(self,):
        return self.redis_client.get(self.url_key)

    def encode_img(self, image_frame: np.ndarray, encoding_method="binary") -> bytes:
        _, buffer = cv2.imencode(".jpg", image_frame)
        if encoding_method == "base64":
            frame_encoded = base64.b64encode(buffer).decode("utf-8")
            return frame_encoded.encode("utf-8")
        elif encoding_method == "binary":
            return buffer.tobytes()
        else:
            raise ValueError("Unsupported encoding method. Use 'binary' or 'base64'.")

    def check_stop_signal(self):
        stop_signal = self.redis_client.get("stop_signal")
        if stop_signal == "1":
            self.redis_client.delete("stop_signal")
            print("Stop signal received. Halting frame processing.")
            return True
        return False

    def capture_frames(self, encoding_method="binary"):
        while True:
            # Check for new camera URL
            new_video_source = self.get_camera_url()
            if new_video_source and new_video_source != self.video_source:
                self.video_source = new_video_source
                print(f"New camera URL received: {self.video_source}")
                self.redis_client.delete("camera_url")

            if not self.video_source:
                print("Waiting for a valid camera URL...")
                time.sleep(1)
                continue

            # Start capturing frames
            cap = cv2.VideoCapture(self.video_source)
            no_frame_count = 0
            self.timer.start("read")

            while True:
                if self.check_stop_signal():
                    break
                ret, frame = cap.read()
                if not ret:
                    no_frame_count += 1
                    print("No frames from camera, retrying...")
                    time.sleep(0.1)
                    if no_frame_count >= 5:
                        print("Camera disconnected, switching to URL wait mode.")
                        self.timer.stop("read")
                        self.timer.print_summary()
                        self.video_source = None
                        break
                    continue
                else:
                    no_frame_count = 0

                image_bytes = self.encode_img(frame, encoding_method=encoding_method)
                self.redis_client.lpush(self.output_queue, image_bytes)

            # Release the camera and wait for a new URL
            cap.release()
            self.video_source = None
            print("All frames processed. Waiting for a new camera URL...")
            while not self.get_camera_url():
                time.sleep(1)


if __name__ == "__main__":
    processor = FrameProcessor(output_queue="frames_camera1", url_key="camera_url")
    processor.capture_frames(encoding_method="binary")
    # set camera_url rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10
