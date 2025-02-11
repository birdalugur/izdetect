import redis
from abc import ABC, abstractmethod


class BaseClass(ABC):
    redis_client = redis.Redis(host="localhost", port=6379)

    def __init__(self, redis_client: redis.Redis = None):
        if redis_client:
            self.redis_client = redis_client

    @abstractmethod
    def run(self):
        pass
