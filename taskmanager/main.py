import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from taskmanager.auth import oauth2_scheme
from taskmanager.config import settings
from taskmanager.database import close_pool, create_tables, init_pool
from taskmanager.dependencies import get_current_user_from_service, get_service
from taskmanager.exceptions import credentials_exception
from taskmanager.schemas import (
    CreateTask,
    StatusFilter,
    Task,
    Token,
    UpdateTask,
    UserInDB,
)
from taskmanager.service import Service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    await create_tables()
    yield
    await close_pool()


app = FastAPI(lifespan=lifespan)


@app.post("/auth/login")
async def login_for_tokens(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[Service, Depends(get_service)],
) -> Token:
    user = await service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception
    access_token_expires = timedelta(
        minutes=settings.EXPIRE_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = service.create_access_token(
        {"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/auth/register")
async def registration(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    service: Annotated[Service, Depends(get_service)],
):
    user = await service._auth_repository.get_user(username)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    password_hash = service.get_password_hash(password)
    user = await service._auth_repository.create_user(username, password_hash)
    return user


# @app.post("/auth/refresh")


@app.post("/tasks", response_model=Task)
async def create_task(
    task: CreateTask,
    service: Annotated[Service, Depends(get_service)],
    user: Annotated[UserInDB, Depends(get_current_user_from_service)],
) -> Task:
    return await service.create_task(task, user)


@app.get("/tasks", response_model=list[Task])
async def get_tasks(
    service: Annotated[Service, Depends(get_service)],
    user: Annotated[UserInDB, Depends(get_current_user_from_service)],
    status: str | None = None,
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
