# app/config.py
import os
from typing import List

class Config:
    OUTPUT_FOLDER: str = os.path.abspath("data/")
    CAMERA_URL: str = "http://10.100.10.94/axis-cgi/mjpg/video.cgi?resolution=1280x800&fps=10"
    RTSP_URL: str = "rtsp://deneme:155115@10.100.10.94:554/axis-media/media.amp?adjustablelivestream=1&fps=10"
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
    CHANNEL_NAME: str = "event_channel"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:3000","http://10.100.17.72:3000","http://10.100.17.52:8000"]
    LABEL_MAP: dict = {1: "insan", 2: "arac", 3: "hayvan"}

    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

    

# Ensure output folder exists
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)