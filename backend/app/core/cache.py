"""
Redis cache configuration
"""
import json
import redis.asyncio as redis
from typing import Optional, Any
from app.core.config import settings

redis_client: Optional[redis.Redis] = None


async def init_redis():
    """
    Initialize Redis connection
    """
    global redis_client
    if settings.REDIS_ENABLED:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )


async def close_redis():
    """
    Close Redis connection
    """
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_cache() -> Optional[redis.Redis]:
    """
    Get Redis cache instance
    """
    return redis_client


async def set_cache(key: str, value: Any, expire: int = 300):
    """
    Set cache value
    """
    if redis_client:
        try:
            await redis_client.setex(
                key,
                expire,
                json.dumps(value) if not isinstance(value, str) else value
            )
        except Exception as e:
            logger.error(f"Error setting cache: {e}")


async def get_cache_value(key: str) -> Optional[Any]:
    """
    Get cache value
    """
    if redis_client:
        value = await redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
    return None


async def delete_cache(key: str):
    """
    Delete cache key
    """
    if redis_client:
        await redis_client.delete(key)
