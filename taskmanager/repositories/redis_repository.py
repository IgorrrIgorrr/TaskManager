from datetime import timedelta

import redis.asyncio as aioredis  # type: ignore


class RedisRepository:
    def __init__(self):
        self.redis = aioredis.from_url("redis://redis-db:6379", decode_responses=True)

    async def store_refresh_token_in_redis(
        self, user_id: int | None, token: str, expires_days: timedelta
    ):
        await self.redis.setex(f"refresh_token:{user_id}", expires_days * 86400, token)

    async def validate_refresh_token_in_redis(
        self, user_id: int | None, token: str
    ) -> bool:
        stored_token = await self.redis.get(f"refresh_token:{user_id}")
        return stored_token == token

    async def delete_refresh_token_in_redis(self, user_id: int):
        await self.redis.delete(f"refresh_token:{user_id}")
