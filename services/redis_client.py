from typing import List, Dict, Union
import redis
import json


class RedisClient:
    def __init__(self, host: str, port: int):
        self.client = redis.StrictRedis(host=host, port=port)

    def pop_from_queue(
        self, queue_name: str, count: int = 1
    ) -> Union[bytes, List[bytes]]:
        return self.client.rpop(queue_name, count)

    def push_to_queue(self, queue_name: str, items: List[bytes]) -> None:
        self.client.lpush(queue_name, *items)


def publish_to_redis(data):
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    try:
        message = json.dumps(data, default=str)
        redis_client.publish("event_channel", message)
    except Exception as e:
        print(f"Error publishing to Redis: {e}")
