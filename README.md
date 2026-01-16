# Interval-Scheduler-API
Interval Scheduler API is a FastAPI service that stores time-bounded tasks and builds an optimal, conflict-free schedule. You can create, list, and delete tasks, then call /schedule to pick the highest total priority set of non-overlapping intervals. /schedule/preview runs the same optimization on a one-off payload without saving. Includes /health.

## Run this project

```bash
bash -lc 'set -euo pipefail

# 1) Go to project folder (edit this path if needed)
cd "/Users/alok/Desktop/Interval Scheduler API"

# 2) Create + activate venv
python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv
source .venv/bin/activate

# 3) Install deps
python -m pip install -U pip
python -m pip install -e ".[dev]"

# 4) Run tests
pytest

# 5) Start server in background + wait until ready
API_HOST=127.0.0.1
PORT=8000
API="http://${API_HOST}:${PORT}"
smart-scheduler --host "$API_HOST" --port "$PORT" >/tmp/smart_scheduler.log 2>&1 & PID=$!
trap "kill $PID 2>/dev/null || true" EXIT INT TERM
until curl -sf "$API/health" >/dev/null; do sleep 0.2; done

# 6) Demo calls (terminal)
echo "== health =="; curl -s "$API/health" | python -m json.tool

echo "== add T1 =="; curl -s -X POST "$API/tasks" -H "Content-Type: application/json" \
  -d "{\"task_id\":\"T1\",\"start\":\"2026-01-16T10:00:00+05:30\",\"end\":\"2026-01-16T11:00:00+05:30\",\"priority\":10}" | python -m json.tool

echo "== add T2 =="; curl -s -X POST "$API/tasks" -H "Content-Type: application/json" \
  -d "{\"task_id\":\"T2\",\"start\":\"2026-01-16T10:30:00+05:30\",\"end\":\"2026-01-16T12:00:00+05:30\",\"priority\":15}" | python -m json.tool

echo "== list =="; curl -s "$API/tasks" | python -m json.tool

echo "== schedule =="; curl -s -X POST "$API/schedule" | python -m json.tool

echo "== preview =="; curl -s -X POST "$API/schedule/preview" -H "Content-Type: application/json" \
  -d "{\"tasks\":[{\"task_id\":\"A\",\"start\":\"2026-01-16T10:00:00+05:30\",\"end\":\"2026-01-16T11:00:00+05:30\",\"priority\":10},{\"task_id\":\"B\",\"start\":\"2026-01-16T10:30:00+05:30\",\"end\":\"2026-01-16T12:00:00+05:30\",\"priority\":15},{\"task_id\":\"C\",\"start\":\"2026-01-16T12:00:00+05:30\",\"end\":\"2026-01-16T13:00:00+05:30\",\"priority\":9}]}" | python -m json.tool

# 7) Clear tasks (cleanup)
echo "== clear tasks ==";
for id in $(curl -s "$API/tasks" | python -c "import sys,json; print(\" \".join([t[\"task_id\"] for t in json.load(sys.stdin)]))"); do
  curl -s -X DELETE "$API/tasks/$id" >/dev/null
done

echo "Done. Server stopped. Logs: /tmp/smart_scheduler.log"
