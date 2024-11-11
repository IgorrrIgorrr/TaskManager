import redis.asyncio as aioredis  # type: ignore

redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)


class RedisRepository:

    @staticmethod
    async def store_refresh_token_in_redis(user_id: int, token: str, expires_days: int):
        await redis.setex(f"refresh_token:{user_id}", expires_days, token)

    @staticmethod
    async def validate_refresh_token_in_redis(user_id: int | None, token: str) -> bool:
        stored_token = await redis.get(f"refresh_token:{user_id}")
        return stored_token == token

    @staticmethod
    async def delete_refresh_token_in_redis(user_id: int):
        await redis.delete(f"refresh_token:{user_id}")
