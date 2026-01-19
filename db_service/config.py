import os

class Config:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongodb:27017/")
    OUTPUT_FOLDER = os.environ.get("OUTPUT_FOLDER", "/app/data")
    DB_NAME = os.environ.get("DB_NAME", "object_detection")

    # Ensure output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
