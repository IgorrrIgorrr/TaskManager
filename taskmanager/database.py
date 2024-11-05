import asyncpg

from taskmanager.config import settings

_pool = None


async def init_pool():
    global _pool
    if not _pool:
        _pool = await asyncpg.create_pool(settings.DATABASE_URL)


async def get_pool():
    if not _pool:
        raise RuntimeError("Pool wasn't initialized")
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def create_tables():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password_hash VARCHAR(128) NOT NULL
            );"""
        )

        await conn.execute(
            """CREATE TABLE IF NOT EXISTS tasks(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(50) NOT NULL,
                user_id INTEGER NOT NULL,
                CONSTRAINT fk_users
                    FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );"""
        )
