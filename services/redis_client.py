import json
import redis
import os

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def publish_to_redis(data):
    try:
        message = json.dumps(data, default=str)
        redis_client.publish("event_channel", message)
    except Exception as e:
        print(f"Error publishing to Redis: {e}")
