"""Storage services for Todo application."""

from .storage import (
    tasks,
    tasks_by_id,
    next_id,
    add_task,
    get_task,
    get_all_tasks,
    update_task,
    delete_task,
    toggle_complete,
)

__all__ = [
    "tasks",
    "tasks_by_id",
    "next_id",
    "add_task",
    "get_task",
    "get_all_tasks",
    "update_task",
    "delete_task",
    "toggle_complete",
]
