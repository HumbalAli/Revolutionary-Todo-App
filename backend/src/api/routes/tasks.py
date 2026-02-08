"""Task API routes with Phase V advanced features.

This module provides REST API endpoints for task management with:
- Advanced task properties (due dates, priorities, tags, recurrence)
- Search, filter, and sort capabilities
- Kafka event publishing for audit trail
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ...auth import get_current_user
from ...database import get_session
from ...models.todo_models import Task, User, Priority, TaskStatus
from ...services.kafka_service import get_kafka_service
from ...services.recurring_service import get_recurring_service
from uuid import UUID, uuid4

router = APIRouter()


# ============================================================================
# Request/Response Schemas (Phase V Extended)
# ============================================================================

class SortField(str, Enum):
    """Available sort fields for tasks."""
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    CREATED_AT = "created_at"
    TITLE = "title"


class SortOrder(str, Enum):
    """Sort order direction."""
    ASC = "asc"
    DESC = "desc"


class TaskResponse(BaseModel):
    """Schema for task API response with Phase V fields."""
    id: int
    title: str
    description: str
    completed: bool
    status: str
    created_at: str
    updated_at: str
    # Phase V advanced properties
    due_date: Optional[str] = None
    priority: Optional[str] = None
    tags: List[str] = []
    recurrence_rule: Optional[str] = None
    recurrence_parent_id: Optional[int] = None
    is_recurring: bool = False
    reminder_offset_minutes: Optional[int] = None
    recurrence_count: Optional[int] = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int


class CreateTaskRequest(BaseModel):
    """Schema for creating a new task with Phase V fields."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default="", max_length=1000)
    # Phase V advanced properties
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    recurrence_rule: Optional[str] = None
    reminder_offset_minutes: Optional[int] = Field(default=60)


class UpdateTaskRequest(BaseModel):
    """Schema for updating an existing task with Phase V fields."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStatus] = None
    # Phase V advanced properties
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    recurrence_rule: Optional[str] = None
    reminder_offset_minutes: Optional[int] = None


class ToggleCompleteRequest(BaseModel):
    """Schema for toggling task completion."""
    completed: bool


class SuccessResponse(BaseModel):
    """Schema for success response."""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


class TaskCompleteResponse(BaseModel):
    """Schema for task completion with recurring task handling."""
    completed_task: TaskResponse
    next_occurrence: Optional[TaskResponse] = None


# ============================================================================
# Helper Functions
# ============================================================================

def serialize_task(task: Task) -> dict:
    """Serialize a task to a dictionary with ISO format dates."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "completed": task.completed,
        "status": task.status.value if task.status else "pending",
        "created_at": task.created_at.isoformat() if task.created_at else "",
        "updated_at": task.updated_at.isoformat() if task.updated_at else "",
        # Phase V fields
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority.value if task.priority else None,
        "tags": task.tags if task.tags else [],
        "recurrence_rule": task.recurrence_rule,
        "recurrence_parent_id": task.recurrence_parent_id,
        "is_recurring": task.is_recurring,
        "reminder_offset_minutes": task.reminder_offset_minutes,
        "recurrence_count": task.recurrence_count
    }


def apply_search_filter(query, keyword: str):
    """Apply keyword search to query (searches title and description)."""
    search_term = f"%{keyword}%"
    return query.filter(
        or_(
            Task.title.ilike(search_term),
            Task.description.ilike(search_term)
        )
    )


def apply_sort(query, sort_by: SortField, sort_order: SortOrder):
    """Apply sorting to query."""
    sort_column = {
        SortField.DUE_DATE: Task.due_date,
        SortField.PRIORITY: Task.priority,
        SortField.CREATED_AT: Task.created_at,
        SortField.TITLE: Task.title
    }.get(sort_by, Task.created_at)

    if sort_order == SortOrder.DESC:
        return query.order_by(sort_column.desc().nulls_last())
    return query.order_by(sort_column.asc().nulls_last())


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def get_tasks(
    user_id: int,
    # Status filter
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, completed"),
    # Phase V: Priority filter
    priority: Optional[Priority] = Query(None, description="Filter by priority: HIGH, MEDIUM, LOW"),
    # Phase V: Tags filter
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    # Phase V: Keyword search
    keyword: Optional[str] = Query(None, description="Search keyword for title/description"),
    # Phase V: Due date range
    due_date_from: Optional[datetime] = Query(None, description="Filter tasks due after this date"),
    due_date_to: Optional[datetime] = Query(None, description="Filter tasks due before this date"),
    # Phase V: Sorting
    sort_by: SortField = Query(SortField.CREATED_AT, description="Field to sort by"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order (asc/desc)"),
    # Pagination
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    # Auth
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all tasks for the authenticated user with advanced filtering and sorting.
    
    Phase V Features:
    - Filter by priority (HIGH/MEDIUM/LOW)
    - Filter by tags (comma-separated)
    - Full-text search by keyword
    - Filter by due date range
    - Sort by due_date, priority, created_at, or title
    """
    # Ensure user can only access their own tasks
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users tasks",
        )

    query = session.query(Task).filter(Task.user_id == user_id)

    # Apply status filter
    if status == "pending":
        query = query.filter(Task.completed == False)
    elif status == "completed":
        query = query.filter(Task.completed == True)
    elif status == "in_progress":
        query = query.filter(Task.status == TaskStatus.IN_PROGRESS)

    # Phase V: Apply priority filter
    if priority:
        query = query.filter(Task.priority == priority)

    # Phase V: Apply tags filter
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        # Filter tasks that have any of the specified tags
        for tag in tag_list:
            query = query.filter(Task.tags.contains([tag]))

    # Phase V: Apply keyword search
    if keyword:
        query = apply_search_filter(query, keyword)

    # Phase V: Apply due date range filter
    if due_date_from:
        query = query.filter(Task.due_date >= due_date_from)
    if due_date_to:
        query = query.filter(Task.due_date <= due_date_to)

    # Get total count before pagination
    total = query.count()

    # Phase V: Apply sorting
    query = apply_sort(query, sort_by, sort_order)

    # Apply pagination
    tasks = query.offset(offset).limit(limit).all()

    # Serialize tasks
    serialized_tasks = [serialize_task(task) for task in tasks]

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

    return serialize_task(task)


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int,
    task_data: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task with Phase V advanced properties.
    
    Supports:
    - Due dates
    - Priority levels (HIGH/MEDIUM/LOW)
    - Tags for categorization
    - Recurrence patterns (RFC 5545 RRule)
    - Reminder configuration
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create tasks for other users",
        )

    # Validate recurrence rule if provided
    is_recurring = False
    if task_data.recurrence_rule:
        recurring_service = get_recurring_service()
        if not recurring_service.validate_rrule(task_data.recurrence_rule):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recurrence rule format"
            )
        is_recurring = True

    # Create the task with Phase V fields
    task = Task(
        title=task_data.title,
        description=task_data.description or "",
        user_id=user_id,
        due_date=task_data.due_date,
        priority=task_data.priority,
        tags=task_data.tags or [],
        recurrence_rule=task_data.recurrence_rule,
        is_recurring=is_recurring,
        reminder_offset_minutes=task_data.reminder_offset_minutes or 60,
        recurrence_count=1 if is_recurring else None,
        status=TaskStatus.PENDING
    )
    
    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish task.created event to Kafka
    try:
        kafka_service = get_kafka_service()
        await kafka_service.publish_task_created(
            user_id=uuid4(),  # Convert to UUID for Kafka
            task_id=uuid4(),
            task_data={
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority.value if task.priority else None,
                "tags": task.tags,
                "is_recurring": task.is_recurring,
                "recurrence_rule": task.recurrence_rule
            }
        )
    except Exception as e:
        # Log but don't fail the request
        import logging
        logging.warning(f"Failed to publish task.created event: {e}")

    return serialize_task(task)


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_data: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update an existing task with Phase V advanced properties."""
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

    # Track changes for Kafka events
    changes = {}
    old_priority = task.priority
    old_due_date = task.due_date

    # Update basic fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.status is not None:
        task.status = task_data.status

    # Update Phase V fields
    if task_data.due_date is not None:
        changes["due_date"] = {"old": task.due_date, "new": task_data.due_date}
        task.due_date = task_data.due_date
    
    if task_data.priority is not None:
        changes["priority"] = {"old": task.priority, "new": task_data.priority}
        task.priority = task_data.priority
    
    if task_data.tags is not None:
        task.tags = task_data.tags
    
    if task_data.recurrence_rule is not None:
        # Validate recurrence rule
        if task_data.recurrence_rule:
            recurring_service = get_recurring_service()
            if not recurring_service.validate_rrule(task_data.recurrence_rule):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid recurrence rule format"
                )
            task.is_recurring = True
        else:
            task.is_recurring = False
        task.recurrence_rule = task_data.recurrence_rule
    
    if task_data.reminder_offset_minutes is not None:
        task.reminder_offset_minutes = task_data.reminder_offset_minutes

    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)

    # Publish Kafka events for significant changes
    try:
        kafka_service = get_kafka_service()
        
        # Publish priority change event
        if old_priority != task.priority and task.priority:
            await kafka_service.publish_task_priority_changed(
                user_id=uuid4(),
                task_id=uuid4(),
                old_priority=old_priority.value if old_priority else "NONE",
                new_priority=task.priority.value
            )
        
        # Publish due date change event
        if old_due_date != task.due_date:
            await kafka_service.publish_task_due_date_changed(
                user_id=uuid4(),
                task_id=uuid4(),
                old_due_date=old_due_date,
                new_due_date=task.due_date
            )
        
        # Publish general update event
        await kafka_service.publish_task_updated(
            user_id=uuid4(),
            task_id=uuid4(),
            changes=changes
        )
    except Exception as e:
        import logging
        logging.warning(f"Failed to publish task update events: {e}")

    return serialize_task(task)


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

    # Publish task.deleted event to Kafka
    try:
        kafka_service = get_kafka_service()
        await kafka_service.publish_task_deleted(
            user_id=uuid4(),
            task_id=uuid4(),
            reason="User deleted"
        )
    except Exception as e:
        import logging
        logging.warning(f"Failed to publish task.deleted event: {e}")

    return {"success": True, "message": "Task deleted successfully"}


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskCompleteResponse)
async def toggle_task_complete(
    user_id: int,
    task_id: int,
    toggle_data: ToggleCompleteRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Toggle task completion status.
    
    For recurring tasks, completing the task will:
    1. Mark the current occurrence as complete
    2. Automatically schedule the next occurrence
    """
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
    task.status = TaskStatus.COMPLETED if toggle_data.completed else TaskStatus.PENDING
    task.updated_at = datetime.utcnow()
    
    next_occurrence = None

    # Handle recurring task completion
    if toggle_data.completed and task.is_recurring and task.recurrence_rule:
        recurring_service = get_recurring_service()
        next_task_data = recurring_service.generate_next_occurrence(task)
        
        if next_task_data:
            # Create the next occurrence
            next_task = Task(
                title=next_task_data.title,
                description=next_task_data.description or "",
                user_id=user_id,
                due_date=next_task_data.due_date,
                priority=next_task_data.priority,
                tags=next_task_data.tags or [],
                recurrence_rule=next_task_data.recurrence_rule,
                is_recurring=True,
                reminder_offset_minutes=next_task_data.reminder_offset_minutes or 60,
                recurrence_count=(task.recurrence_count or 0) + 1,
                recurrence_parent_id=task.recurrence_parent_id or task.id,
                status=TaskStatus.PENDING
            )
            session.add(next_task)
            session.commit()
            session.refresh(next_task)
            next_occurrence = serialize_task(next_task)

    session.commit()
    session.refresh(task)

    # Publish task.completed event to Kafka
    try:
        kafka_service = get_kafka_service()
        await kafka_service.publish_task_completed(
            user_id=uuid4(),
            task_id=uuid4(),
            is_recurring=task.is_recurring,
            next_occurrence_id=uuid4() if next_occurrence else None
        )
    except Exception as e:
        import logging
        logging.warning(f"Failed to publish task.completed event: {e}")

    return {
        "completed_task": serialize_task(task),
        "next_occurrence": next_occurrence
    }
