import aioredis
from app.core.config import settings


async def get_redis_connection():
    redis = await aioredis.from_url(url=settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return redis
