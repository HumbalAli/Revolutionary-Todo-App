"""Task dataclass for in-memory todo application.

This module defines the Task entity with attributes for tracking todo items.
"""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a todo item with core attributes.

    Attributes:
        id (int): Unique identifier (sequential from 1)
        title (str): Task title (required, non-empty)
        description (str): Optional task details
        completed (bool): Completion status (defaults to False)
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False