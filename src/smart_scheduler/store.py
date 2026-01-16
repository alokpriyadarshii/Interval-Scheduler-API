from __future__ import annotations

from threading import RLock
from typing import Dict, List, Optional

from .models import Task


class TaskStore:
    """Thread-safe in-memory task store."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._tasks: Dict[str, Task] = {}

    def upsert(self, task: Task) -> None:
        with self._lock:
            self._tasks[task.task_id] = task

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._tasks.get(task_id)

    def delete(self, task_id: str) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None

    def list(self) -> List[Task]:
        with self._lock:
            return list(self._tasks.values())

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()
