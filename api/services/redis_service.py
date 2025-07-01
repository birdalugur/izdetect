# app/services/redis_service.py
import json
import redis
from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
from typing import AsyncGenerator
from fastapi import Request
from config import Config

class RedisService:
    def __init__(self):
        self.client = SyncRedis(
            host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True
        )
        self.async_client: AsyncRedis | None = None

    async def get_async_client(self) -> AsyncRedis:
        if self.async_client is None:
            self.async_client = AsyncRedis(
                host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True
            )
        return self.async_client

    def publish(self, channel: str, message: str):
        self.client.publish(channel, message)

    def set(self, key: str, value: str):
        self.client.set(key, value)

    def delete(self, key: str):
        self.client.delete(key)

    def rpush(self, key: str, *values):
        self.client.rpush(key, *values)

    async def event_generator(self, request: Request, channel: str, map_labels) -> AsyncGenerator[str, None]:
        redis_client = await self.get_async_client()
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
                if message:
                    message_data = json.loads(message["data"])
                    message_data = map_labels(message_data, Config.LABEL_MAP)
                    yield f"data: {json.dumps(message_data)}\n\n"
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await redis_client.close()
