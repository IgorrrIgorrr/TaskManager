from taskmanager.database import get_pool
from taskmanager.schemas import UserInDB


class AuthRepository:

    async def get_user(self, username: str) -> UserInDB | None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, username, password_hash from users
                WHERE username = $1
                """,
                username,
            )
            if row:
                user_dict = dict(row)
                return UserInDB(**user_dict)
            return None

    async def create_user(self, username: str, password_hash: str) -> UserInDB | None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                    INSERT INTO users(username, password_hash)
                    VALUES($1, $2)
                    RETURNING id, username, password_hash
                    """,
                username,
                password_hash,
            )
            if row:
                user_dict = dict(row)
                return UserInDB(**user_dict)
            return None
