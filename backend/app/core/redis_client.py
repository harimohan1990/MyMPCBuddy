import json
from typing import Optional, Any
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

_redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> Optional[aioredis.Redis]:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=3.0,
            )
            # Ping test
            await _redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection unavailable ({str(e)}). Operating in in-memory fallback mode.")
            _redis_client = None
    return _redis_client


class RedisCacheManager:
    """
    Manages caching, rate limiting, and session keys in Redis.
    """

    @staticmethod
    async def get_json(key: str) -> Optional[Any]:
        client = await get_redis_client()
        if not client:
            return None
        try:
            val = await client.get(key)
            return json.loads(val) if val else None
        except Exception:
            return None

    @staticmethod
    async def set_json(key: str, value: Any, ttl_seconds: int = 300) -> bool:
        client = await get_redis_client()
        if not client:
            return False
        try:
            await client.set(key, json.dumps(value), ex=ttl_seconds)
            return True
        except Exception:
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        client = await get_redis_client()
        if not client:
            return False
        try:
            await client.delete(key)
            return True
        except Exception:
            return False

    @staticmethod
    async def publish_event(channel: str, event_data: dict) -> bool:
        client = await get_redis_client()
        if not client:
            return False
        try:
            await client.publish(channel, json.dumps(event_data))
            return True
        except Exception:
            return False
