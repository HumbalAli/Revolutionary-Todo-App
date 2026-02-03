"""MCP Tools for AI-powered task management"""

from typing import List, Optional
from sqlmodel import Session, select
from ..models.todo_models import Task, User
from ..database import engine
from pydantic import BaseModel


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: int


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: str
    updated_at: str


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

        # Create new task
        task = Task(
            title=request.title,
            description=request.description,
            user_id=request.user_id,
            completed=False
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
            updated_at=task.updated_at.isoformat() if task.updated_at else ""
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
                updated_at=task.updated_at.isoformat() if task.updated_at else ""
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
            updated_at=task.updated_at.isoformat() if task.updated_at else ""
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

        session.add(task)
        session.commit()
        session.refresh(task)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat() if task.created_at else "",
            updated_at=task.updated_at.isoformat() if task.updated_at else ""
        )