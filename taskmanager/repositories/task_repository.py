from typing import Union

from taskmanager.database import get_pool
from taskmanager.schemas import CreateTask, StatusFilter, Task, UpdateTask, UserInDB


class TaskRepository:

    async def create_task(self, task: CreateTask, user: UserInDB) -> Task:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO tasks(name, description, status, user_id)
                VALUES($1, $2, $3, $4)
                RETURNING id, name, description, status, user_id
                """,
                task.name,
                task.description,
                task.status,
                user.id,
            )
        return Task(**row)

    async def get_tasks(self, status: str | None = None) -> list[Task]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            query = "SELECT id, name, description, status FROM tasks"
            if status:
                query += " WHERE status = $1"
                rows = await conn.fetch(query, status)
            else:
                rows = await conn.fetch(query)
            return [Task(**row) for row in rows]

    async def update_task(self, task_id: int, update_info: UpdateTask) -> Task:
        pool = await get_pool()
        async with pool.acquire() as conn:
            update_fields = []
            values: list[str | int] = []
            if update_info.name is not None:
                update_fields.append("name = $1")
                values.append(update_info.name)
            if update_info.description is not None:
                update_fields.append("description = $2")
                values.append(update_info.description)
            if update_info.status is not None:
                update_fields.append("status = $3")
                values.append(update_info.status)

            if not update_fields:
                raise ValueError("No fields to update")

            sql = f"""
                UPDATE tasks
                SET {', '.join(update_fields)}
                WHERE id = ${len(values)+1}
                RETURNING id, name, description, status
                """
            values.append(task_id)

            row = await conn.fetchrow(sql, *values)

        if not row:
            raise ValueError("Task not found")

        return Task(**row)

    async def delete_task(self, task_id: int) -> dict:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM tasks
                WHERE id = $1
                """,
                task_id,
            )
            if "DELETE 0" in result:
                raise ValueError(f"Task with id {task_id} does not exist")
        return {"message": f"task with id {task_id} was deleted"}
