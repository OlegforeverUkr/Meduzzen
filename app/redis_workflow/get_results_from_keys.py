from app.db.connect_redis import get_redis_connection


async def get_data_by_quiz_id(quiz_id):
    redis = await get_redis_connection()
    data = []
    keys = await redis.keys(f"*:{quiz_id}:*")
    for key in keys:
        value = await redis.get(key)
        data.append(value)
    redis.close()
    return data


async def get_data_by_company_id(company_id):
    redis = await get_redis_connection()
    data = []
    keys = await redis.keys(f"*:*:{company_id}")
    for key in keys:
        value = await redis.get(key)
        data.append(value)
    redis.close()
    return data


async def get_data_by_user_id(user_id):
    redis = await get_redis_connection()
    data = []
    keys = await redis.keys(f"{user_id}:*:*")
    for key in keys:
        value = await redis.get(key)
        data.append(value)
    redis.close()
    return data