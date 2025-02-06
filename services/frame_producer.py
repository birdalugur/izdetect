import cv2
import redis
import time
from image_processor import ImageProcessor


class FrameProducer:
    def __init__(self, video_source: str, output_queue: str, redis_client: redis.Redis):
        self.video_source = video_source
        self.output_queue = output_queue
        self.redis_client = redis_client
        self.stop_signal = False

    def __repr__(self):
        return (
            f"FrameProducer(output_queue={self.output_queue}, "
            f"redis_client={self.redis_client}, "
            f"video_source={self.video_source})"
        )

    def capture_frames(self, encoding_method="binary"):
        cap = cv2.VideoCapture(self.video_source)
        if not cap.isOpened():
            print("Error opening video source.")
            return
        counter = 0
        while not self.stop_signal:
            counter += 1
            no_frame_count = 0
            ret, frame = cap.read()
            if counter == 898:
                print("Video ended.")
            if not ret:
                no_frame_count += 1
                print("No frames from camera, retrying {}...".format(no_frame_count))
                time.sleep(0.1)
                if no_frame_count > 5:
                    print("Camera disconnected, switching to URL wait mode.")
                    self.stop_signal = True
                    break
                else:
                    continue

            image_bytes = ImageProcessor.encode_img(
                frame, encoding_method=encoding_method
            )
            self.redis_client.lpush(self.output_queue, image_bytes)

        cap.release()
        print("All frames processed. Waiting for a new camera URL...")


if __name__ == "__main__":
    video_source = "/home/birdal/izdetect/sahil.mp4"
    output_queue = "frames_camera1"
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

    processor = FrameProducer(
        output_queue=output_queue, video_source=video_source, redis_client=redis_client
    )
    processor.capture_frames(encoding_method="binary")
    # set camera_url rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10
