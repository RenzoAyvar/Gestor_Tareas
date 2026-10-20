from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.models.task_schemas import TaskCreate, TaskResponse, TaskStatus, TaskUpdate
from app.repositories.json_task_repository import JsonTaskRepository
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tareas"])
bearer = HTTPBearer(auto_error=False)


def get_authenticated_owner(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> str:
    owner = (
        decode_access_token(credentials.credentials)
        if credentials is not None and credentials.scheme.lower() == "bearer"
        else None
    )
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return owner


def get_task_service() -> TaskService:
    return TaskService(JsonTaskRepository())


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    owner: Annotated[str, Depends(get_authenticated_owner)],
    service: Annotated[TaskService, Depends(get_task_service)],
    task_status: Annotated[TaskStatus, Query(alias="status")] = "all",
) -> list[TaskResponse]:
    return await service.list_tasks(owner, task_status)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    owner: Annotated[str, Depends(get_authenticated_owner)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    return await service.create_task(owner, payload)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    owner: Annotated[str, Depends(get_authenticated_owner)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    return await service.update_task(owner, task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    owner: Annotated[str, Depends(get_authenticated_owner)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> Response:
    await service.delete_task(owner, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
