import redis
from abc import ABC, abstractmethod


class BaseClass(ABC):
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)

    @abstractmethod
    def run(self):
        pass
