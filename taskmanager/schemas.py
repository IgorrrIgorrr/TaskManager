from pydantic import BaseModel


class CreateTask(BaseModel):
    name: str
    description: str | None = None
    status: str


class Task(BaseModel):
    id: int
    name: str
    description: str | None = None
    status: str

    class Config:
        from_attributes = True


class StatusFilter(BaseModel):
    status: str | None = None


class UpdateTask(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str


class User(BaseModel):
    id: int | None = None
    username: str


class UserInDB(User):
    password_hash: str
