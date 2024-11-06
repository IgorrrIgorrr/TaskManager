from typing import Annotated

from fastapi import Depends

from taskmanager.repositories.task_repository import TaskRepository
from taskmanager.service import Service


def get_task_repository():
    return TaskRepository()


def get_service(task_rep: Annotated[TaskRepository, Depends(get_task_repository)]):
    return Service(task_rep)
