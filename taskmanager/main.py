import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI

from taskmanager.database import close_pool, create_tables, init_pool
from taskmanager.dependencies import get_service
from taskmanager.schemas import CreateTask, StatusFilter, Task, UpdateTask
from taskmanager.service import Service


@asynccontextmanager
async def lifespan():
    await init_pool()
    await create_tables()
    yield
    await close_pool()


app = FastAPI(lifespan=lifespan)


@app.post("/tasks", response_model=Task)
async def create_task(
    task: CreateTask, service: Annotated[Service, Depends(get_service)]
) -> Task:
    return await service.create_task(task)


@app.get("/tasks", response_model=list[Task])
async def get_tasks(
    service: Annotated[Service, Depends(get_service)],
    status: StatusFilter | None = None,
) -> list[Task]:
    return await service.get_tasks(status)


@app.put("/tasks/{id}", response_model=Task)
async def update_task(
    id: int, update_info: UpdateTask, service: Annotated[Service, Depends(get_service)]
) -> Task:
    return await service.update_task(id, update_info)


@app.delete("/tasks/{id}", response_model=dict)
async def delete_task(
    id: int, service: Annotated[Service, Depends(get_service)]
) -> dict:
    return await service.delete_task(id)
