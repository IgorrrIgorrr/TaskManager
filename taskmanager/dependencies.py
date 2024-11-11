from typing import Annotated

from fastapi import Depends

from taskmanager.auth import oauth2_scheme
from taskmanager.repositories.auth_repository import AuthRepository
from taskmanager.repositories.redis_repository import RedisRepository
from taskmanager.repositories.task_repository import TaskRepository
from taskmanager.schemas import UserInDB
from taskmanager.service import Service


def get_task_repository():
    return TaskRepository()


def get_auth_repository():
    return AuthRepository()


def get_redis_repository():
    return RedisRepository()


def get_service(
    task_rep: Annotated[TaskRepository, Depends(get_task_repository)],
    auth_rep: Annotated[AuthRepository, Depends(get_auth_repository)],
    redis_rep: Annotated[RedisRepository, Depends(get_redis_repository)],
):
    return Service(task_rep, auth_rep, redis_rep)


async def get_current_user_from_service(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[Service, Depends(get_service)],
) -> UserInDB:
    user = await service.get_current_user(token)
    return user
