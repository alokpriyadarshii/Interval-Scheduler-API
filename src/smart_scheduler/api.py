from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .algo import ScheduleResult, weighted_interval_schedule
from .models import Task
from .store import TaskStore


class TaskIn(BaseModel):
    task_id: Optional[str] = Field(default=None, description="If omitted, a UUID will be generated")
    start: datetime
    end: datetime
    priority: int = Field(ge=0)
    meta: Optional[Dict[str, Any]] = None


class TaskOut(BaseModel):
    task_id: str
    start: datetime
    end: datetime
    priority: int
    meta: Optional[Dict[str, Any]] = None


class ScheduleOut(BaseModel):
    total_priority: int
    tasks: List[TaskOut]


class PreviewIn(BaseModel):
    tasks: List[TaskIn]


def _to_task(t: TaskIn) -> Task:
    tid = t.task_id or str(uuid4())
    try:
        return Task(task_id=tid, start=t.start, end=t.end, priority=t.priority, meta=t.meta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _task_to_out(t: Task) -> TaskOut:
    return TaskOut(task_id=t.task_id, start=t.start, end=t.end, priority=t.priority, meta=t.meta)


def _result_to_out(res: ScheduleResult) -> ScheduleOut:
    return ScheduleOut(total_priority=res.total_priority, tasks=[_task_to_out(t) for t in res.tasks])


def create_app(store: Optional[TaskStore] = None) -> FastAPI:
    store = store or TaskStore()
    app = FastAPI(title="Smart Scheduler", version="0.1.0")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/tasks", response_model=TaskOut)
    def add_task(task: TaskIn) -> TaskOut:
        t = _to_task(task)
        store.upsert(t)
        return _task_to_out(t)

    @app.get("/tasks", response_model=List[TaskOut])
    def list_tasks() -> List[TaskOut]:
        return [_task_to_out(t) for t in store.list()]

    @app.delete("/tasks/{task_id}")
    def delete_task(task_id: str) -> Dict[str, Any]:
        ok = store.delete(task_id)
        if not ok:
            raise HTTPException(status_code=404, detail="task not found")
        return {"deleted": task_id}

    @app.post("/schedule", response_model=ScheduleOut)
    def schedule() -> ScheduleOut:
        res = weighted_interval_schedule(store.list())
        return _result_to_out(res)

    @app.post("/schedule/preview", response_model=ScheduleOut)
    def schedule_preview(payload: PreviewIn) -> ScheduleOut:
        tasks = [_to_task(t) for t in payload.tasks]
        res = weighted_interval_schedule(tasks)
        return _result_to_out(res)

    return app


app = create_app()
