import json
import time
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback in-memory dictionary cache store
_memory_cache = {}


class RedisCacheManager:
    def __init__(self):
        self.redis_client = None
        self.use_redis = False

    async def connect(self):
        try:
            import redis.asyncio as aioredis
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1.5
            )
            await self.redis_client.ping()
            self.use_redis = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Redis not available ({e}). Falling back to In-Memory cache.")
            self.use_redis = False

    async def get(self, key: str) -> Optional[Any]:
        if self.use_redis and self.redis_client:
            try:
                val = await self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.error(f"Redis get error for {key}: {e}")

        # In-memory fallback lookup
        if key in _memory_cache:
            entry = _memory_cache[key]
            if entry["expires_at"] > time.time():
                return entry["value"]
            else:
                del _memory_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 600):
        val_str = json.dumps(value, default=str)

        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.set(key, val_str, ex=ttl_seconds)
                return
            except Exception as e:
                logger.error(f"Redis set error for {key}: {e}")

        # In-memory fallback
        _memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds
        }

    async def delete(self, key: str):
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception:
                pass
        _memory_cache.pop(key, None)


cache_manager = RedisCacheManager()
