import asyncpg

from taskmanager.config import settings

_pool = None


async def init_pool():
    global _pool
    if not _pool:
        _pool = await asyncpg.create_pool(settings.DATABASE_URL)


async def get_pool():
    if not _pool:
        raise RuntimeError("Pool wasn't initialised")
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
