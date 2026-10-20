from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status

from app.models.task_schemas import TaskCreate, TaskResponse, TaskStatus, TaskUpdate
from app.repositories.json_task_repository import JsonTaskRepository

TASK_NOT_FOUND = "Tarea no encontrada."


class TaskService:
    def __init__(self, repository: JsonTaskRepository) -> None:
        self.repository = repository

    async def list_tasks(self, owner: str, task_status: TaskStatus) -> list[TaskResponse]:
        tasks = await self.repository.list_for_owner(owner)
        if task_status == "pending":
            tasks = [task for task in tasks if not task.get("completada", False)]
        elif task_status == "completed":
            tasks = [task for task in tasks if task.get("completada", False)]
        return [TaskResponse.model_validate(task) for task in tasks]

    async def create_task(self, owner: str, data: TaskCreate) -> TaskResponse:
        task = {
            "id": str(uuid4()),
            "titulo": data.titulo,
            "descripcion": data.descripcion,
            "fecha_limite": data.fecha_limite.isoformat() if data.fecha_limite else None,
            "completada": False,
            "creada_en": datetime.now(timezone.utc).isoformat(),
            "propietario": owner,
        }
        return TaskResponse.model_validate(await self.repository.add(task))

    async def update_task(
        self, owner: str, task_id: str, data: TaskUpdate
    ) -> TaskResponse:
        task = await self.repository.update_for_owner(
            task_id, owner, {"completada": data.completada}
        )
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND)
        return TaskResponse.model_validate(task)

    async def delete_task(self, owner: str, task_id: str) -> None:
        if not await self.repository.delete_for_owner(task_id, owner):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND)
