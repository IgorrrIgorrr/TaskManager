import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from taskmanager.database import close_pool, create_tables, init_pool


@asynccontextmanager
async def lifespan():
    await init_pool()
    await create_tables()
    yield
    await close_pool()


app = FastAPI(lifespan=lifespan)
