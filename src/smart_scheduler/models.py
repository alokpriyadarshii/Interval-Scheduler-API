from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True, slots=True)
class Task:
    """A task with a fixed interval and a priority (weight).

    Intervals are interpreted as half-open: [start, end).
    """

    task_id: str
    start: datetime
    end: datetime
    priority: int
    meta: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if _is_aware(self.start) != _is_aware(self.end):
            raise ValueError("start and end must both be timezone-aware or both naive")
        if self.end <= self.start:
            raise ValueError("end must be strictly after start")
        if self.priority < 0:
            raise ValueError("priority must be non-negative")


def _is_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None
