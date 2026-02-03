"""In-memory storage service for todo application.

This module provides CRUD operations and task management using
in-memory data structures (list for iteration, dict for O(1) lookup).
"""

from typing import List, Dict, Optional
from models.task import Task


# In-memory storage
tasks: List[Task] = []
tasks_by_id: Dict[int, Task] = {}
next_id: int = 1


def add_task(title: str, description: str = "") -> Task:
    """Add a new task to storage.

    Args:
        title: Task title (required, non-empty)
        description: Optional task details

    Returns:
        Newly created Task with auto-generated ID

    Raises:
        ValueError: If title is empty
    """
    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")

    global next_id
    task = Task(id=next_id, title=title.strip(), description=description.strip())
    next_id += 1

    tasks.append(task)
    tasks_by_id[task.id] = task

    return task


def get_task(task_id: int) -> Optional[Task]:
    """Retrieve a task by ID.

    Args:
        task_id: Unique task identifier

    Returns:
        Task if found, None otherwise
    """
    return tasks_by_id.get(task_id)


def get_all_tasks() -> List[Task]:
    """Retrieve all tasks.

    Returns:
        List of all tasks in order of creation
    """
    return tasks.copy()


def update_task(task_id: int, title: Optional[str] = None,
                description: Optional[str] = None) -> Optional[Task]:
    """Update an existing task.

    Args:
        task_id: Unique task identifier
        title: New title (optional, if provided must be non-empty)
        description: New description (optional)

    Returns:
        Updated task if found, None otherwise

    Raises:
        ValueError: If title is provided but empty
    """
    task = get_task(task_id)
    if not task:
        return None

    if title is not None:
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        task.title = title.strip()

    if description is not None:
        task.description = description.strip()

    return task


def delete_task(task_id: int) -> bool:
    """Delete a task from storage.

    Args:
        task_id: Unique task identifier

    Returns:
        True if task was deleted, False if not found
    """
    task = get_task(task_id)
    if not task:
        return False

    tasks.remove(task)
    del tasks_by_id[task_id]

    return True


def toggle_complete(task_id: int) -> Optional[Task]:
    """Toggle the completion status of a task.

    Args:
        task_id: Unique task identifier

    Returns:
        Updated task if found, None otherwise
    """
    task = get_task(task_id)
    if not task:
        return None

    task.completed = not task.completed
    return task
