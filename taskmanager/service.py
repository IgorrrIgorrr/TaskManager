from schemas import CreateTask

from taskmanager.repositories.task_repository import (
    StatusFilter,
    Task,
    TaskRepository,
    UpdateTask,
)


class Service:
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def create_task(self, task: CreateTask) -> Task:
        return await self._task_repository.create_task(task)

    async def get_tasks(self, status: StatusFilter) -> list[Task]:
        return await self._task_repository.get_tasks(status)

    async def update_task(self, task_id: int, update_info: UpdateTask) -> Task:
        return await self._task_repository.update_task(task_id, update_info)

    async def delete_task(self, task_id: int) -> dict:
        return await self._task_repository.delete_task(task_id)
