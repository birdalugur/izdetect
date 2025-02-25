import json
import redis

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


def publish_to_redis(data):
    try:
        message = json.dumps(data, default=str)
        redis_client.publish("event_channel", message)
    except Exception as e:
        print(f"Error publishing to Redis: {e}")
