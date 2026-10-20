import asyncio
import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")

_locks: dict[Path, asyncio.Lock] = {}


def _default_tasks_file() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "tasks.json"


class JsonTaskRepository:
    def __init__(self, file_path: str | Path | None = None) -> None:
        configured = file_path or os.getenv("TASKS_FILE") or _default_tasks_file()
        self.file_path = Path(configured).expanduser().resolve()
        self._lock = _locks.setdefault(self.file_path, asyncio.Lock())

    async def list_for_owner(self, owner: str) -> list[dict[str, Any]]:
        async with self._lock:
            tasks = self._read()
            return [task.copy() for task in tasks if task.get("propietario") == owner]

    async def add(self, task: dict[str, Any]) -> dict[str, Any]:
        def mutation(tasks: list[dict[str, Any]]) -> dict[str, Any]:
            tasks.append(task.copy())
            return task.copy()

        return await self._mutate(mutation)

    async def update_for_owner(
        self, task_id: str, owner: str, changes: dict[str, Any]
    ) -> dict[str, Any] | None:
        def mutation(tasks: list[dict[str, Any]]) -> dict[str, Any] | None:
            for task in tasks:
                if task.get("id") == task_id and task.get("propietario") == owner:
                    task.update(changes)
                    return task.copy()
            return None

        return await self._mutate(mutation)

    async def delete_for_owner(self, task_id: str, owner: str) -> bool:
        def mutation(tasks: list[dict[str, Any]]) -> bool:
            for index, task in enumerate(tasks):
                if task.get("id") == task_id and task.get("propietario") == owner:
                    tasks.pop(index)
                    return True
            return False

        return await self._mutate(mutation)

    async def _mutate(self, mutation: Callable[[list[dict[str, Any]]], T]) -> T:
        async with self._lock:
            # El archivo es deliberadamente pequeño y local. Mantener la operación
            # dentro del lock evita que otra coroutine lea un JSON a medio reemplazar.
            return self._mutate_sync(mutation)

    def _mutate_sync(self, mutation: Callable[[list[dict[str, Any]]], T]) -> T:
        tasks = self._read()
        result = mutation(tasks)
        self._write_atomic(tasks)
        return result

    def _read(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []
        with self.file_path.open("r", encoding="utf-8") as source:
            content = json.load(source)
        if not isinstance(content, list):
            raise ValueError("El archivo de tareas debe contener una lista JSON")
        return content

    def _write_atomic(self, tasks: list[dict[str, Any]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            dir=self.file_path.parent, prefix=f".{self.file_path.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as target:
                json.dump(tasks, target, ensure_ascii=False, indent=2)
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary_name, self.file_path)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
