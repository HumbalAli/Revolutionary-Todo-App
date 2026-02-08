"""Event subscription API routes for real-time updates.

This module provides REST API endpoints for:
- Subscribing to task events
- Getting event history (audit log)
- Managing event subscriptions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from ...auth import get_current_user
from ...database import get_session
from ...models.todo_models import User
from ...models.event_models import TaskEvent, TaskEventResponse

router = APIRouter()


# ============================================================================
# Request/Response Schemas
# ============================================================================

class EventListResponse(BaseModel):
    """Schema for paginated event list response."""
    events: List[TaskEventResponse]
    total: int
    limit: int
    offset: int


class EventSubscription(BaseModel):
    """Schema for event subscription configuration."""
    event_types: List[str] = Field(
        default=["task.created", "task.updated", "task.completed", "task.deleted"],
        description="Event types to subscribe to"
    )
    include_data: bool = Field(
        default=True,
        description="Whether to include full event data"
    )


class SubscriptionResponse(BaseModel):
    """Schema for subscription confirmation."""
    subscription_id: str
    user_id: int
    event_types: List[str]
    created_at: str


# ============================================================================
# In-memory store for WebSocket connections (for MVP)
# In production, use Redis or similar for distributed systems
# ============================================================================

class ConnectionManager:
    """WebSocket connection manager for real-time event delivery."""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.subscriptions: Dict[int, EventSubscription] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_event(self, user_id: int, event: Dict[str, Any]):
        """Send an event to all connections for a user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(event)
                except Exception:
                    pass
    
    async def broadcast(self, event: Dict[str, Any]):
        """Broadcast an event to all connected users."""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(event)
                except Exception:
                    pass


# Global connection manager
connection_manager = ConnectionManager()


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/{user_id}/events", response_model=EventListResponse)
async def get_events(
    user_id: int,
    # Event type filter
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g., task.created)"),
    # Task filter
    task_id: Optional[int] = Query(None, description="Filter by task ID"),
    # Date range
    from_date: Optional[datetime] = Query(None, description="Events after this date"),
    to_date: Optional[datetime] = Query(None, description="Events before this date"),
    # Pagination
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    # Auth
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get event history (audit log) for the authenticated user.
    
    Provides a paginated list of all task-related events including:
    - task.created
    - task.updated
    - task.completed
    - task.deleted
    - task.priority_changed
    - task.due_date_changed
    - task.recurrence_updated
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users events",
        )
    
    # Convert user_id to UUID for query
    user_uuid = UUID(int=user_id)
    
    query = session.query(TaskEvent).filter(TaskEvent.user_id == user_uuid)
    
    # Apply filters
    if event_type:
        query = query.filter(TaskEvent.event_type == event_type)
    
    if task_id:
        task_uuid = UUID(int=task_id)
        query = query.filter(TaskEvent.task_id == task_uuid)
    
    if from_date:
        query = query.filter(TaskEvent.timestamp >= from_date)
    
    if to_date:
        query = query.filter(TaskEvent.timestamp <= to_date)
    
    # Get total count
    total = query.count()
    
    # Order by timestamp descending and paginate
    events = query.order_by(TaskEvent.timestamp.desc()).offset(offset).limit(limit).all()
    
    # Serialize events
    serialized_events = [
        {
            "id": str(event.id),
            "event_type": event.event_type,
            "schema_version": event.schema_version,
            "timestamp": event.timestamp.isoformat(),
            "user_id": str(event.user_id),
            "task_id": str(event.task_id),
            "data": event.data
        }
        for event in events
    ]
    
    return {
        "events": serialized_events,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{user_id}/events/recent")
async def get_recent_events(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get the most recent events for quick overview."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users events",
        )
    
    user_uuid = UUID(int=user_id)
    
    events = session.query(TaskEvent).filter(
        TaskEvent.user_id == user_uuid
    ).order_by(
        TaskEvent.timestamp.desc()
    ).limit(limit).all()
    
    return {
        "events": [
            {
                "id": str(event.id),
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "task_id": str(event.task_id),
                "summary": _get_event_summary(event)
            }
            for event in events
        ]
    }


@router.get("/{user_id}/events/stats")
async def get_event_stats(
    user_id: int,
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get event statistics for the specified time period."""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users events",
        )
    
    user_uuid = UUID(int=user_id)
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Get event counts by type
    from sqlalchemy import func
    from datetime import timedelta
    
    stats = session.query(
        TaskEvent.event_type,
        func.count(TaskEvent.id).label("count")
    ).filter(
        TaskEvent.user_id == user_uuid,
        TaskEvent.timestamp >= from_date
    ).group_by(
        TaskEvent.event_type
    ).all()
    
    return {
        "period_days": days,
        "from_date": from_date.isoformat(),
        "to_date": datetime.utcnow().isoformat(),
        "event_counts": {
            stat.event_type: stat.count for stat in stats
        },
        "total_events": sum(stat.count for stat in stats)
    }


@router.websocket("/{user_id}/events/stream")
async def event_stream(
    websocket: WebSocket,
    user_id: int,
):
    """WebSocket endpoint for real-time event streaming.
    
    Connect to this endpoint to receive task events in real-time.
    Events are automatically pushed when tasks are created, updated,
    completed, or deleted.
    """
    await connection_manager.connect(websocket, user_id)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Successfully connected to event stream"
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_json()
                
                # Handle subscription updates
                if data.get("type") == "subscribe":
                    event_types = data.get("event_types", [])
                    connection_manager.subscriptions[user_id] = EventSubscription(
                        event_types=event_types
                    )
                    await websocket.send_json({
                        "type": "subscribed",
                        "event_types": event_types
                    })
                
                # Handle ping/pong for connection keep-alive
                elif data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    finally:
        connection_manager.disconnect(websocket, user_id)


# ============================================================================
# Helper Functions
# ============================================================================

def _get_event_summary(event: TaskEvent) -> str:
    """Generate a human-readable summary for an event."""
    summaries = {
        "task.created": "Task created",
        "task.updated": "Task updated",
        "task.completed": "Task completed",
        "task.deleted": "Task deleted",
        "task.priority_changed": f"Priority changed to {event.data.get('new_priority', 'unknown')}",
        "task.due_date_changed": "Due date updated",
        "task.recurrence_updated": "Recurrence pattern changed",
        "reminder.due": "Reminder sent",
        "reminder.sent": "Reminder delivered"
    }
    return summaries.get(event.event_type, event.event_type)


async def broadcast_task_event(user_id: int, event_type: str, task_data: Dict[str, Any]):
    """Broadcast a task event to connected WebSocket clients.
    
    This function is called by other services when task events occur.
    
    Args:
        user_id: User to send the event to
        event_type: Type of event
        task_data: Event payload
    """
    event = {
        "type": "task_event",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": task_data
    }
    
    # Check subscription filters
    if user_id in connection_manager.subscriptions:
        sub = connection_manager.subscriptions[user_id]
        if event_type not in sub.event_types:
            return
    
    await connection_manager.send_event(user_id, event)


# Export for use by other modules
__all__ = ["router", "connection_manager", "broadcast_task_event"]
