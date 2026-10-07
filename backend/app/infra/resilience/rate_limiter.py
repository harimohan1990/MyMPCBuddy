import time
from typing import Tuple, Optional
from app.core.redis_client import get_redis_client
from app.core.logging import logger


class RateLimiter:
    """
    Sliding window rate limiter backed by Redis.
    Falls back to an in-memory dictionary if Redis is offline.
    """

    _in_memory_buckets: dict[str, list[float]] = {}

    @classmethod
    async def check_rate_limit(
        cls,
        key: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> Tuple[bool, int, int]:
        """
        Returns: (allowed: bool, remaining_requests: int, reset_seconds: int)
        """
        now = time.time()
        client = await get_redis_client()

        if client:
            try:
                pipe = client.pipeline()
                bucket_key = f"rate_limit:{key}"
                clear_before = now - window_seconds
                # Remove timestamps older than window
                pipe.zremrangebyscore(bucket_key, 0, clear_before)
                # Count remaining timestamps
                pipe.zcard(bucket_key)
                # Add current timestamp
                pipe.zadd(bucket_key, {str(now): now})
                # Set expire on bucket
                pipe.expire(bucket_key, window_seconds)
                results = await pipe.execute()

                current_count = results[1]
                allowed = current_count < max_requests
                remaining = max(0, max_requests - current_count - 1)
                return allowed, remaining, window_seconds
            except Exception as e:
                logger.warning(f"Redis rate limiter failed: {e}. Falling back to in-memory.")

        # In-memory fallback
        if key not in cls._in_memory_buckets:
            cls._in_memory_buckets[key] = []

        timestamps = cls._in_memory_buckets[key]
        clear_before = now - window_seconds
        cls._in_memory_buckets[key] = [t for t in timestamps if t > clear_before]

        if len(cls._in_memory_buckets[key]) >= max_requests:
            return False, 0, window_seconds

        cls._in_memory_buckets[key].append(now)
        remaining = max_requests - len(cls._in_memory_buckets[key])
        return True, remaining, window_seconds
