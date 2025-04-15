import os
import redis
from abc import ABC, abstractmethod


class BaseClass(ABC):
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    def __init__(self, redis_client: redis.Redis = None):
        if redis_client:
            self.redis_client = redis_client

    @abstractmethod
    def run(self):
        pass
