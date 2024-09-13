import redis
import json
from functools import wraps
from app.core.config import settings

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs)}"
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator