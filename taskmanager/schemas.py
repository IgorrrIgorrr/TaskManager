from pydantic import Basemodel


class CreateTask(Basemodel):
    name: str
    description: str | None = None
    status: str


class Task(Basemodel):
    id: int
    name: str
    description: str | None = None
    status: str

    class Config:
        from_attributes = True


class StatusFilter(Basemodel):
    status: str | None = None


class UpdateTask(Basemodel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
