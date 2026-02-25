from functools import wraps
import redis.asyncio as redis

class CacheLayer:
    def __init__(self, redis_url: str | None = None):
        self.redis = redis.from_url(redis_url) if redis_url else None
        self._local: dict = {}

    async def get_or_fetch(self, key: str, fetcher, ttl: int = 3600):
        if self.redis:
            cached = await self.redis.get(key)
            if cached:
                return cached
        elif key in self._local:
            return self._local[key]

        result = await fetcher()

        if self.redis:
            await self.redis.setex(key, ttl, result)
        else:
            self._local[key] = result

        return result