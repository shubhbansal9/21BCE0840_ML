import redis
import json
from app.core.config import settings

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)

    def get(self, key):
        value = self.redis_client.get(key)
        if value:
            try:
                return json.loads(value.decode('utf-8'))
            except json.JSONDecodeError:
                return value.decode('utf-8')
        return None

    def set(self, key, value, expiration=3600):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.redis_client.setex(key, expiration, value)

cache = RedisCache()
