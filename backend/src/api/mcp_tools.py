"""MCP Tools for AI-powered task management"""


from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from ..models.todo_models import Task, User, Priority, TaskStatus
from ..database import engine
from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: int
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    recurrence_rule: Optional[str] = None
    reminder_offset_minutes: Optional[int] = 60


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    recurrence_rule: Optional[str] = None
    reminder_offset_minutes: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: str
    updated_at: str
    due_date: Optional[str] = None
    priority: Optional[str] = None
    tags: List[str] = []
    recurrence_rule: Optional[str] = None
    is_recurring: bool = False


class TaskFilterRequest(BaseModel):
    user_id: int
    status: Optional[str] = None  # "all", "pending", "completed"


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]


def add_task(request: TaskCreateRequest) -> TaskResponse:
    """Create a new task"""
    with Session(engine) as session:
        # Get the user
        user = session.get(User, request.user_id)
        if not user:
            raise ValueError(f"User with id {request.user_id} not found")

        # Determine if recurring
        is_recurring = bool(request.recurrence_rule)

        # Create new task
        task = Task(
            title=request.title,
            description=request.description,
            user_id=request.user_id,
            completed=False,
            due_date=request.due_date,
            priority=request.priority,
            tags=request.tags or [],
            recurrence_rule=request.recurrence_rule,
            is_recurring=is_recurring,
            reminder_offset_minutes=request.reminder_offset_minutes
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat() if task.created_at else "",
            updated_at=task.updated_at.isoformat() if task.updated_at else "",
            due_date=task.due_date.isoformat() if task.due_date else None,
            priority=task.priority.value if task.priority else None,
            tags=task.tags,
            recurrence_rule=task.recurrence_rule,
            is_recurring=task.is_recurring
        )


def list_tasks(request: TaskFilterRequest) -> TaskListResponse:
    """Retrieve tasks for a user with optional filtering"""
    with Session(engine) as session:
        # Build query
        query = select(Task).where(Task.user_id == request.user_id)

        if request.status == "pending":
            query = query.where(Task.completed == False)
        elif request.status == "completed":
            query = query.where(Task.completed == True)

        tasks = session.exec(query).all()

        task_responses = []
        for task in tasks:
            task_responses.append(TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                created_at=task.created_at.isoformat() if task.created_at else "",
                updated_at=task.updated_at.isoformat() if task.updated_at else "",
                due_date=task.due_date.isoformat() if task.due_date else None,
                priority=task.priority.value if task.priority else None,
                tags=task.tags,
                recurrence_rule=task.recurrence_rule,
                is_recurring=task.is_recurring
            ))

        return TaskListResponse(tasks=task_responses)


def complete_task(user_id: int, task_id: int, completed: bool) -> TaskResponse:
    """Mark a task as complete or incomplete"""
    with Session(engine) as session:
        # Get the task
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        # Verify task belongs to user
        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")

        # Update task
        task.completed = completed
        session.add(task)
        session.commit()
        session.refresh(task)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat() if task.created_at else "",
            updated_at=task.updated_at.isoformat() if task.updated_at else "",
            due_date=task.due_date.isoformat() if task.due_date else None,
            priority=task.priority.value if task.priority else None,
            tags=task.tags,
            recurrence_rule=task.recurrence_rule,
            is_recurring=task.is_recurring
        )


def delete_task(user_id: int, task_id: int) -> dict:
    """Delete a task"""
    with Session(engine) as session:
        # Get the task
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        # Verify task belongs to user
        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")

        # Delete task
        session.delete(task)
        session.commit()

        return {"message": "Task deleted successfully", "task_id": task_id}


def update_task(user_id: int, task_id: int, request: TaskUpdateRequest) -> TaskResponse:
    """Update a task's details"""
    with Session(engine) as session:
        # Get the task
        task = session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        # Verify task belongs to user
        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")

        # Update fields if provided
        if request.title is not None:
            task.title = request.title
        if request.description is not None:
            task.description = request.description
        if request.completed is not None:
            task.completed = request.completed
        if request.due_date is not None:
            task.due_date = request.due_date
        if request.priority is not None:
            task.priority = request.priority
        if request.tags is not None:
            task.tags = request.tags
        if request.recurrence_rule is not None:
            task.recurrence_rule = request.recurrence_rule
            task.is_recurring = bool(request.recurrence_rule)
        if request.reminder_offset_minutes is not None:
            task.reminder_offset_minutes = request.reminder_offset_minutes

        session.add(task)
        session.commit()
        session.refresh(task)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat() if task.created_at else "",
            updated_at=task.updated_at.isoformat() if task.updated_at else "",
            due_date=task.due_date.isoformat() if task.due_date else None,
            priority=task.priority.value if task.priority else None,
            tags=task.tags,
            recurrence_rule=task.recurrence_rule,
            is_recurring=task.is_recurring
        )