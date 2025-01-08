import aioredis
import asyncio
import json
import datetime

async def publish_to_redis():
    redis = await aioredis.from_url("redis://localhost:6379")
    try:
        for i in range(1, 11):  # 1'den 10'a kadar döngü
            data = {
                "frame_count": i,
                "image_url": "hello world",
                "labels": [{"1": 3}, {"2": 3}],
                "status": "active",
                "time": datetime.datetime.now().isoformat(),
                "_id": "677e59ea08511e3b5a059b"
            }
            message = json.dumps(data)
            await redis.publish("event_channel", message)
            await asyncio.sleep(0.1)
    finally:
        await redis.close()

asyncio.run(publish_to_redis())
