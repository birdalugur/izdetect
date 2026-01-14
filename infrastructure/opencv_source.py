import cv2
import os
from typing import Any
from core.interfaces import VideoSource

class OpenCVVideoSource(VideoSource):
    def __init__(self, source: str, timeout_ms: int = 5000):
        self.source = source
        self.timeout_ms = timeout_ms
        self.cap = None
        # Configure timeout via env var as per requirements
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = f"timeout;{timeout_ms}"

    def open(self) -> bool:
        self.cap = cv2.VideoCapture(self.source)
        return self.cap.isOpened()

    def read(self) -> tuple[bool, Any]:
        if not self.cap:
            return False, None
        return self.cap.read()

    def release(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None

    def is_opened(self) -> bool:
        return self.cap.isOpened() if self.cap else False
