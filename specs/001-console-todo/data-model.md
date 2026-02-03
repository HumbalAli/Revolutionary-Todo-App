# Data Model: Phase I - In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Date**: 2025-12-31

## Entity: Task

### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|----------|-------------|
| id | int | Yes | Auto-assigned | Unique identifier (sequential from 1) |
| title | str | Yes | - | Task title, non-empty, non-whitespace |
| description | str | No | "" | Optional task details |
| completed | bool | No | False | Completion status |

### Validation Rules

| Attribute | Rule | Error Message |
|-----------|------|--------------|
| title | Cannot be empty string | "Error: Title cannot be empty" |
| title | Cannot be whitespace-only | "Error: Title cannot be empty" |
| id | Must exist for update/delete/complete | "Error: Task ID not found" |
| id | Must be positive integer | "Error: Invalid task ID" |

### State Transitions

```
Incomplete (completed=False) -- Mark Complete --> Complete (completed=True)
Complete (completed=True)    -- Mark Complete --> Incomplete (completed=False)
```

### Python Data Structure

```python
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
```

### Storage Structures

```python
# Primary storage (for iteration)
tasks: List[Task] = []

# Lookup storage (for O(1) access by ID)
tasks_by_id: Dict[int, Task] = {}

# Next ID counter
next_id: int = 1
```

## Invariants

1. Task IDs are always unique
2. Task IDs are sequential, never re-used
3. Title is always non-empty (after validation)
4. completed is always boolean
5. tasks and tasks_by_id are kept in sync
