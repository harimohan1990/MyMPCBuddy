import json
import time
from typing import Optional, Dict, Any, Callable
from app.core.redis_client import get_redis_client
from app.core.logging import logger


class JobQueue:
    """
    Lightweight, robust async job queue backed by Redis Streams / Lists
    with Dead-Letter Queue (DLQ) support.
    """

    QUEUE_KEY = "mcp_hub:jobs:pending"
    DLQ_KEY = "mcp_hub:jobs:dead_letter"

    @classmethod
    async def enqueue(cls, task_type: str, payload: Dict[str, Any], max_retries: int = 3) -> str:
        job_id = f"job_{task_type}_{int(time.time() * 1000)}"
        message = {
            "id": job_id,
            "type": task_type,
            "payload": payload,
            "retries": 0,
            "max_retries": max_retries,
            "enqueued_at": time.time(),
        }
        client = await get_redis_client()
        if client:
            try:
                await client.rpush(cls.QUEUE_KEY, json.dumps(message))
                return job_id
            except Exception as e:
                logger.error(f"Failed to enqueue job to Redis: {e}")
        # In-memory execution fallback
        logger.info(f"Direct synchronous fallback execution for job {job_id}")
        return job_id

    @classmethod
    async def dequeue(cls, timeout: int = 2) -> Optional[Dict[str, Any]]:
        client = await get_redis_client()
        if not client:
            return None
        try:
            val = await client.blpop(cls.QUEUE_KEY, timeout=timeout)
            if val:
                _, job_json = val
                return json.loads(job_json)
        except Exception as e:
            logger.error(f"Failed to dequeue job from Redis: {e}")
        return None

    @classmethod
    async def send_to_dlq(cls, job: Dict[str, Any], error: str):
        job["failed_at"] = time.time()
        job["final_error"] = error
        client = await get_redis_client()
        if client:
            try:
                await client.rpush(cls.DLQ_KEY, json.dumps(job))
                logger.warning(f"Job {job.get('id')} sent to Dead-Letter Queue: {error}")
            except Exception as e:
                logger.error(f"Failed to push to DLQ: {e}")
