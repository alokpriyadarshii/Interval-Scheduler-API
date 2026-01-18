from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Sequence, Tuple

from .models import Task


@dataclass(frozen=True, slots=True)
class ScheduleResult:
    tasks: List[Task]
    total_priority: int


def weighted_interval_schedule(tasks: Iterable[Task]) -> ScheduleResult:
    """Return an optimal non-overlapping subset of tasks.

    This implements **Weighted Interval Scheduling**:
    - Sort by end time
    - For each task i, compute p[i] = rightmost task ending <= task[i].start
    - DP: dp[i] = max(dp[i-1], weight[i] + dp[p[i]])

    Tie-breaking: if equal score, prefer the solution with fewer tasks ending later
    by using a stable ordering (end, start, task_id).
    """

    task_list = list(tasks)
    if not task_list:
        return ScheduleResult(tasks=[], total_priority=0)

     timezone_flags = {t.start.tzinfo is not None and t.start.tzinfo.utcoffset(t.start) is not None for t in task_list}
    if len(timezone_flags) > 1:
        raise ValueError("cannot mix naive and timezone-aware datetimes")
        
    # Stable deterministic sort: end, start, id
    task_list.sort(key=lambda t: (t.end, t.start, t.task_id))

    ends: List[datetime] = [t.end for t in task_list]

    # Binary search helper
    def rightmost_compatible_index(start: datetime) -> int:
        lo, hi = 0, len(ends) - 1
        ans = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if ends[mid] <= start:
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans

    p: List[int] = [rightmost_compatible_index(t.start) for t in task_list]

    # dp[i] stores best score considering tasks[0..i]
    dp: List[int] = [0] * len(task_list)
    choose: List[bool] = [False] * len(task_list)

    for i, t in enumerate(task_list):
        incl = t.priority + (dp[p[i]] if p[i] != -1 else 0)
        excl = dp[i - 1] if i > 0 else 0

        if incl > excl:
            dp[i] = incl
            choose[i] = True
        elif incl < excl:
            dp[i] = excl
            choose[i] = False
        else:
            # Tie-breaker: prefer earlier-ending solutions by excluding
            # the current (later-ending) task in a stable ordering.
            dp[i] = excl
            choose[i] = False

    selected: List[Task] = []
    i = len(task_list) - 1
    while i >= 0:
        if choose[i]:
            # Check if taking i is consistent with dp
            t = task_list[i]
            incl = t.priority + (dp[p[i]] if p[i] != -1 else 0)
            excl = dp[i - 1] if i > 0 else 0
            if incl >= excl:
                selected.append(t)
                i = p[i]
                continue
        i -= 1

    selected.reverse()
    return ScheduleResult(tasks=selected, total_priority=dp[-1])
