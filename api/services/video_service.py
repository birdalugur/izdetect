# app/services/video_service.py
import cv2
from fastapi import HTTPException
from typing import Generator

class VideoService:
    @staticmethod
    def generate_frames(rtsp_url: str, camera_id: str) -> Generator[bytes, None, None]:
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail=f"Failed to connect to RTSP stream for camera {camera_id}")
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    raise HTTPException(status_code=500, detail=f"Failed to capture frame for camera {camera_id}")
                _, buffer = cv2.imencode(".jpg", frame)
                frame_bytes = buffer.tobytes()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
        finally:
            cap.release()