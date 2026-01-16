# Interval-Scheduler-API
Interval Scheduler API is a FastAPI service that stores time-bounded tasks and builds an optimal, conflict-free schedule. You can create, list, and delete tasks, then call /schedule to pick the highest total priority set of non-overlapping intervals. /schedule/preview runs the same optimization on a one-off payload without saving. Includes /health.
