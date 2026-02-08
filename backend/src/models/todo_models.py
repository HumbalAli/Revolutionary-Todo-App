"""Todo models for task management.

Phase V: Extended with advanced task properties including:
- Due dates and priorities
- Tags for categorization
- Recurrence patterns (RFC 5545 RRule)
- Reminder settings
- Full-text search support
"""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskStatus(str, Enum):
    """Task status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)
    name: str = Field(nullable=False, max_length=255)


class User(UserBase, table=True):
    """
    User model representing an authenticated user with associated tasks.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tasks: List["Task"] = Relationship(back_populates="user")


class TaskBase(SQLModel):
    """Base task model with core properties."""
    title: str = Field(nullable=False, min_length=1, max_length=255)
    description: Optional[str] = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)

    # T023: Phase V - Due date and priority fields
    due_date: Optional[datetime] = Field(default=None, index=True)
    priority: Optional[Priority] = Field(default=None, index=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON, default=[]))

    # T024: Phase V - Recurrence fields
    recurrence_rule: Optional[str] = Field(default=None, max_length=500)
    recurrence_parent_id: Optional[int] = Field(default=None, foreign_key="task.id")
    is_recurring: bool = Field(default=False)

    # T025: Phase V - Reminder and recurrence tracking
    reminder_offset_minutes: Optional[int] = Field(default=60)
    recurrence_count: Optional[int] = Field(default=None)

    # Task status (extended from simple completed boolean)
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)


class Task(TaskBase, table=True):
    """
    Task model representing a todo item with core and advanced attributes.

    Phase V additions:
    - due_date: When the task should be completed
    - priority: HIGH, MEDIUM, or LOW priority level
    - tags: Array of user-defined tags for categorization
    - recurrence_rule: RFC 5545 RRule string for recurring tasks
    - recurrence_parent_id: Links to original task for recurring instances
    - is_recurring: Flag indicating if this is a recurring task
    - reminder_offset_minutes: Minutes before due_date to send reminder
    - recurrence_count: Current occurrence number for recurring tasks
    - status: Task status (pending, in_progress, completed)
    - search_vector: Full-text search vector (handled by database trigger)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # T026: Phase V - Full-text search vector
    # Note: This is managed by a database trigger that combines title and description
    # The actual column type is TSVECTOR, handled in migration
    # search_vector: Optional[str] = Field(default=None, sa_column_kwargs={"type_": "TSVECTOR"})

    # Relationship to User
    user: Optional[User] = Relationship(back_populates="tasks")

    # Self-referential relationship for recurring tasks
    recurrence_parent: Optional["Task"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "Task.id",
            "foreign_keys": "[Task.recurrence_parent_id]"
        }
    )


# Pydantic schemas for API requests/responses

class TaskCreate(SQLModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default="", max_length=1000)

    # Phase V: Advanced properties
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    recurrence_rule: Optional[str] = None
    reminder_offset_minutes: Optional[int] = Field(default=60)


class TaskUpdate(SQLModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    status: Optional[TaskStatus] = None

    # Phase V: Advanced properties
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    recurrence_rule: Optional[str] = None
    reminder_offset_minutes: Optional[int] = None


class TaskResponse(SQLModel):
    """Schema for task API response."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    status: TaskStatus
    user_id: int
    created_at: datetime
    updated_at: datetime

    # Phase V: Advanced properties
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    tags: List[str] = Field(default_factory=list)
    recurrence_rule: Optional[str] = None
    recurrence_parent_id: Optional[int] = None
    is_recurring: bool = False
    reminder_offset_minutes: Optional[int] = None
    recurrence_count: Optional[int] = None

    class Config:
        from_attributes = True


class TaskListResponse(SQLModel):
    """Schema for paginated task list response."""
    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int


class TaskCompleteResponse(SQLModel):
    """Schema for task completion response (includes next occurrence for recurring)."""
    completed_task: TaskResponse
    next_occurrence: Optional[TaskResponse] = None