import redis
from app.core.config import settings

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)

    def get(self, key):
        value = self.redis_client.get(key)
        return value.decode('utf-8') if value else None

    def set(self, key, value, expiration=3600):
        self.redis_client.setex(key, expiration, value)

cache = RedisCache()