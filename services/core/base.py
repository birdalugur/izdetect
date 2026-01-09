import os
import redis
from abc import ABC, abstractmethod


class Service(ABC):
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    # Keep a default connection if needed, but instance injection is better
    _default_redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

    def __init__(self, redis_client: redis.Redis = None):
        self.redis_client = redis_client if redis_client else self._default_redis_client

    @abstractmethod
    def run(self):
        """Main execution loop for the service."""
        pass

    @abstractmethod
    def stop(self):
        """Signals the service to stop."""
        pass
