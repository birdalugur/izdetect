
from pymongo import MongoClient
from .config import config

class Database:
    client: MongoClient = None
    db = None

    def connect(self):
        self.client = MongoClient(config.MONGO_URI)
        self.db = self.client[config.MONGO_DB]
        print(f"Connected to MongoDB at {config.MONGO_URI}")

    def close(self):
        if self.client:
            self.client.close()

db = Database()

def get_db():
    return db.db
