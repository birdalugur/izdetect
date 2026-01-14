import redis
import json
import os
from typing import Any, Optional
from core.interfaces import MessageBroker

class RedisBroker(MessageBroker):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        # Note: Some services used decode_responses=False for images.
        # We might need two clients or handle bytes specifically.
        # For now, let's assume we handle encoding before sending if needed, or allow raw bytes.
        self.binary_client = redis.Redis(host=host, port=port, db=db, decode_responses=False)

    def publish(self, channel: str, message: str) -> None:
        self.client.publish(channel, message)

    def subscribe(self, channel: str) -> Any:
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        return pubsub

    def lpush(self, key: str, value: Any) -> None:
        # If value is bytes, use binary client, else text client?
        # Or just use binary client for lpush always if we know it's image data?
        # FrameProducer sends image_bytes.
        if isinstance(value, bytes):
            self.binary_client.lpush(key, value)
        else:
            self.client.lpush(key, value)

    def rpop(self, key: str) -> Optional[Any]:
        # Usually we want bytes for images
        return self.binary_client.rpop(key)

    def flush_all(self) -> None:
        self.client.flushall()

    def get_pubsub(self):
        """Helper to get raw pubsub for advanced usage"""
        return self.client.pubsub()
