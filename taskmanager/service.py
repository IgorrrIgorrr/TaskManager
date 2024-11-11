from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends
from jose import jwt
from jose.exceptions import JWTError

from taskmanager.auth import oauth2_scheme, pwd_context
from taskmanager.config import settings
from taskmanager.exceptions import credentials_exception
from taskmanager.repositories.auth_repository import AuthRepository
from taskmanager.repositories.redis_repository import RedisRepository
from taskmanager.repositories.task_repository import TaskRepository
from taskmanager.schemas import (
    CreateTask,
    StatusFilter,
    Task,
    Token,
    TokenData,
    UpdateTask,
    UserInDB,
)


class Service:
    def __init__(
        self,
        task_repository: TaskRepository,
        auth_repository: AuthRepository,
        redis_repository: RedisRepository,
    ):
        self._task_repository = task_repository
        self._auth_repository = auth_repository
        self._redis_repository = redis_repository

    async def create_task(self, task: CreateTask, user: UserInDB) -> Task:
        return await self._task_repository.create_task(task, user)

    async def get_tasks(self, status: str | None = None) -> list[Task]:
        return await self._task_repository.get_tasks(status)

    async def update_task(self, task_id: int, update_info: UpdateTask) -> Task:
        return await self._task_repository.update_task(task_id, update_info)

    async def delete_task(self, task_id: int) -> dict:
        return await self._task_repository.delete_task(task_id)

    @staticmethod
    def verify_password(plain_password, password_hash) -> bool:
        return pwd_context.verify(plain_password, password_hash)

    @staticmethod
    def get_password_hash(password) -> str:
        return pwd_context.hash(password)

    async def authenticate_user(self, username: str, password: str) -> UserInDB | None:
        user = await self._auth_repository.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def get_current_user(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UserInDB:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError as e:
            raise credentials_exception from e
        user = await self._auth_repository.get_user(token_data.username)
        if user is None:
            raise credentials_exception
        return user

    async def refresh_access_token(self, refresh_token: str) -> Token | None:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload is None:
            raise credentials_exception

        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        access_token_expires = timedelta(
            minutes=settings.EXPIRE_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = self.create_access_token(
            {"sub": username}, expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token, token_type="bearer", refresh_token=refresh_token
        )

    async def store_refresh_token_in_redis(
        self, user_id: int, token: str, expires_days: int
    ):
        await self._redis_repository.store_refresh_token_in_redis(
            user_id, token, expires_days
        )

    async def validate_refresh_token_in_redis(
        self, user_id: int | None, token: str
    ) -> bool:
        stored_token = await self._redis_repository.validate_refresh_token_in_redis(
            user_id, token
        )
        return stored_token == token

    async def delete_refresh_token_in_redis(self, user_id: int):
        await self._redis_repository.delete_refresh_token_in_redis(user_id)
