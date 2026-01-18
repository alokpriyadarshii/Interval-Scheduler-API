from __future__ import annotations

from datetime import datetime, timedelta, timezone
from itertools import combinations

from smart_scheduler.algo import weighted_interval_schedule
from smart_scheduler.models import Task


def brute_force_best(tasks: list[Task]) -> int:
    best = 0
    for r in range(len(tasks) + 1):
        for combo in combinations(tasks, r):
            ok = True
            s = sorted(combo, key=lambda t: t.start)
            for a, b in zip(s, s[1:]):
                if a.end > b.start:
                    ok = False
                    break
            if ok:
                best = max(best, sum(t.priority for t in s))
    return best


def test_weighted_interval_schedule_matches_bruteforce() -> None:
    tz = timezone.utc
    base = datetime(2026, 1, 16, tzinfo=tz)

    tasks = [
        Task("T1", base + timedelta(hours=1), base + timedelta(hours=3), 5),
        Task("T2", base + timedelta(hours=2), base + timedelta(hours=5), 6),
        Task("T3", base + timedelta(hours=4), base + timedelta(hours=6), 5),
        Task("T4", base + timedelta(hours=6), base + timedelta(hours=7), 4),
        Task("T5", base + timedelta(hours=5), base + timedelta(hours=8), 11),
        Task("T6", base + timedelta(hours=7), base + timedelta(hours=9), 2),
    ]

    res = weighted_interval_schedule(tasks)
    assert res.total_priority == brute_force_best(tasks)


def test_empty_input() -> None:
    res = weighted_interval_schedule([])
    assert res.total_priority == 0
    assert res.tasks == []
    

def test_mixed_timezone_awareness_rejected() -> None:
    tz = timezone.utc
    aware_start = datetime(2026, 1, 16, 9, tzinfo=tz)
    aware_end = datetime(2026, 1, 16, 10, tzinfo=tz)
    naive_start = datetime(2026, 1, 16, 10)
    naive_end = datetime(2026, 1, 16, 11)

    tasks = [
        Task("T1", aware_start, aware_end, 5),
        Task("T2", naive_start, naive_end, 4),
    ]

    try:
        weighted_interval_schedule(tasks)
    except ValueError as exc:
        assert "timezone" in str(exc)
    else:
        raise AssertionError("Expected ValueError for mixed timezone awareness")
