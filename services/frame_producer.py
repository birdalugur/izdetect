import cv2
import redis
import time
from processing_timer import ProcessingTimer
from image_processor import ImageProcessor


class FrameProducer:
    def __init__(self, output_queue, url_key, redis_client: redis.StrictRedis):
        self.redis_client = redis_client
        self.output_queue = output_queue
        self.url_key = url_key
        self.video_source = None
        self.timer = ProcessingTimer()

    def __repr__(self):
        return (f"FrameProducer(output_queue={self.output_queue}, "
                f"url_key={self.url_key}, "
                f"redis_client={self.redis_client}, "
                f"video_source={self.video_source})")

    def get_camera_url(self):
        return self.redis_client.get(self.url_key)

    def check_stop_signal(self):
        stop_signal = self.redis_client.get("stop_signal")
        if stop_signal == "1":
            self.redis_client.delete("stop_signal")
            print("Stop signal received. Halting frame processing.")
            return True
        return False

    def capture_frames(self, encoding_method="binary"):
        while True:
            if self.url_key is None:
                time.sleep(2)
                print("URL key is not set. Waiting for a valid key...")
                continue

            # Start capturing frames
            cap = cv2.VideoCapture(self.url_key)
            no_frame_count = 0
            self.timer.start("read")

            while True:
                if self.check_stop_signal():
                    print("Stop sinyali alindi.")
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

                image_bytes = ImageProcessor.encode_img(
                    frame, encoding_method=encoding_method
                )
                self.redis_client.lpush(self.output_queue, image_bytes)

            # Release the camera and wait for a new URL
            cap.release()
            self.video_source = None
            print("All frames processed. Waiting for a new camera URL...")
            while not self.get_camera_url():
                time.sleep(1)


if __name__ == "__main__":
    redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
    processor = FrameProducer(output_queue="frames_camera1", url_key="camera_url", redis_client=redis_client)
    processor.capture_frames(encoding_method="binary")
    # set camera_url rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10
