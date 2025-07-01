import cv2
import time
from typing import Generator


class VideoService:
    @staticmethod
    def generate_frames(rtsp_url: str, camera_id: str) -> Generator[bytes, None, None]:
        cap = cv2.VideoCapture(rtsp_url)
        max_consecutive_failures = 5
        failure_count = 0
        reconnect_delay = 2

        if not cap.isOpened():
            print(f"[{camera_id}] Initial connection failed. Retrying...")

        while True:
            if not cap.isOpened():
                cap.open(rtsp_url)
                time.sleep(reconnect_delay)
                failure_count = 0
                continue

            success, frame = cap.read()
            if not success:
                failure_count += 1
                print(
                    f"[{camera_id}] Frame read failed ({failure_count}/{max_consecutive_failures})"
                )

                if failure_count >= max_consecutive_failures:
                    print(
                        f"[{camera_id}] Max consecutive failures reached. Attempting reconnect..."
                    )
                    cap.release()
                    time.sleep(reconnect_delay)
                    cap = cv2.VideoCapture(rtsp_url)
                    failure_count = 0
                continue

            failure_count = 0
            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
