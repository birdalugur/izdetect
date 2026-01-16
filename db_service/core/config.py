
import os

class Config:
    MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
    MONGO_PORT = os.environ.get("MONGO_PORT", "27017")
    MONGO_USER = os.environ.get("MONGO_USER", "")
    MONGO_PASS = os.environ.get("MONGO_PASS", "")
    MONGO_DB = os.environ.get("MONGO_DB", "object_detection")

    @property
    def MONGO_URI(self):
        if self.MONGO_USER and self.MONGO_PASS:
            return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}/"
        else:
            return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/"

config = Config()
