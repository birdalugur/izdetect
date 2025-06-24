# app/services/video_service.py
import cv2
import time
from fastapi import HTTPException
from typing import Generator

class VideoService:
    @staticmethod
    def generate_frames(rtsp_url: str, camera_id: str) -> Generator[bytes, None, None]:
        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            print(f"[{camera_id}] Initial connection failed. Retrying...")
        
        while True:
            if not cap.isOpened():
                cap.open(rtsp_url)
                time.sleep(2)
                continue

            success, frame = cap.read()
            if not success:
                print(f"[{camera_id}] Frame read failed. Attempting reconnect...")
                cap.release()
                time.sleep(2)
                cap = cv2.VideoCapture(rtsp_url)
                continue

            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
