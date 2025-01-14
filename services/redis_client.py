from typing import List, Dict, Union
import redis


class RedisClient:
    def __init__(self, host: str, port: int):
        self.client = redis.StrictRedis(host=host, port=port)

    def pop_from_queue(
        self, queue_name: str, count: int = 1
    ) -> Union[bytes, List[bytes]]:
        return self.client.rpop(queue_name, count)

    def push_to_queue(self, queue_name: str, items: List[bytes]) -> None:
        self.client.lpush(queue_name, *items)
