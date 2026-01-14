from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from ...auth import get_current_user
from ...database import get_session
from ...models.task import Task
from ...models.user import User

router = APIRouter()


from datetime import datetime
from typing import Optional

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int


class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default="", max_length=1000)


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class ToggleCompleteRequest(BaseModel):
    completed: bool


class SuccessResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def get_tasks(
    user_id: int,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all tasks for the authenticated user, optionally filtered by status."""
    # Ensure user can only access their own tasks
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users tasks",
        )

    query = session.query(Task).filter(Task.user_id == user_id)

    if status == "pending":
        query = query.filter(Task.completed == False)
    elif status == "completed":
        query = query.filter(Task.completed == True)

    total = query.count()
    tasks = query.offset(offset).limit(limit).all()

    # Convert datetime objects to ISO format strings for each task
    serialized_tasks = []
    for task in tasks:
        serialized_tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        })

    return {
        "tasks": serialized_tasks,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific task by ID."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users tasks",
        )

    task = session.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Convert datetime objects to ISO format strings
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int,
    task_data: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create tasks for other users",
        )

    task = Task(
        title=task_data.title,
        description=task_data.description or "",
        user_id=user_id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Convert datetime objects to ISO format strings
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_data: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update an existing task."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users tasks",
        )

    task = session.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    session.commit()
    session.refresh(task)

    # Convert datetime objects to ISO format strings
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


@router.delete("/{user_id}/tasks/{task_id}", response_model=SuccessResponse)
async def delete_task(
    user_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a task."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users tasks",
        )

    task = session.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    session.delete(task)
    session.commit()

    return {"success": True, "message": "Task deleted successfully"}


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    user_id: int,
    task_id: int,
    toggle_data: ToggleCompleteRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Toggle task completion status."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other users tasks",
        )

    task = session.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task.completed = toggle_data.completed
    session.commit()
    session.refresh(task)

    # Convert datetime objects to ISO format strings
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }

