from app.db.connect_redis import get_redis_connection


async def save_data_to_redis_db(key, value):
    redis = await get_redis_connection()
    await redis.set(key, value)
    await redis.expire(key, 48 * 3600)


async def get_data_from_redis_db(key):
    redis = await get_redis_connection()
    return await redis.get(key)


async def delete_data_from_redis_db(key):
    redis = await get_redis_connection()
    await redis.delete(key)