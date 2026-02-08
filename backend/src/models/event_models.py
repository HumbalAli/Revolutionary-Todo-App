"""Event models for Kafka/Dapr event-driven architecture.

This module defines the data models for:
- TaskEvent: Audit log events for task operations
- Reminder: Task reminder notifications
- UserProfile: User preferences and settings
- RecurringRule: Recurrence pattern definitions
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField, Column
from sqlalchemy import JSON


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReminderStatus(str, Enum):
    """Reminder delivery status."""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class DeliveryMethod(str, Enum):
    """Reminder delivery methods."""
    EMAIL = "EMAIL"
    PUSH = "PUSH"
    WEBSOCKET = "WEBSOCKET"


class RecurrenceFrequency(str, Enum):
    """Recurrence frequency types."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


# T012: TaskEvent Model
class TaskEvent(SQLModel, table=True):
    """Represents events published to Kafka for audit log and triggering downstream actions.

    Attributes:
        id: Unique identifier for the event
        event_type: Type of event (e.g., task.created, task.completed)
        schema_version: Event schema version for compatibility
        timestamp: When the event occurred
        user_id: User who triggered the event
        task_id: Task related to the event
        data: Event-specific JSON payload
        kafka_partition: Kafka partition where event was published
        kafka_offset: Kafka offset of the event
    """
    __tablename__ = "task_events"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    event_type: str = SQLField(index=True)
    schema_version: str = SQLField(default="1.0")
    timestamp: datetime = SQLField(default_factory=datetime.utcnow, index=True)
    user_id: UUID = SQLField(index=True)
    task_id: UUID = SQLField(index=True)
    data: Dict[str, Any] = SQLField(default_factory=dict, sa_column=Column(JSON))
    kafka_partition: Optional[int] = SQLField(default=None)
    kafka_offset: Optional[int] = SQLField(default=None)


# T013: Reminder Model
class Reminder(SQLModel, table=True):
    """Tracks reminder state to ensure idempotent delivery and audit trail.

    Attributes:
        id: Unique identifier for the reminder
        task_id: Task this reminder is for
        user_id: User to be notified
        scheduled_time: When reminder should be sent
        sent_at: When reminder was actually sent
        status: Current delivery status
        delivery_method: How to deliver the reminder
        retry_count: Number of delivery attempts
        error_message: Error details if delivery failed
    """
    __tablename__ = "reminders"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    task_id: UUID = SQLField(index=True)
    user_id: UUID = SQLField(index=True)
    scheduled_time: datetime = SQLField(index=True)
    sent_at: Optional[datetime] = SQLField(default=None)
    status: ReminderStatus = SQLField(default=ReminderStatus.PENDING, index=True)
    delivery_method: DeliveryMethod = SQLField(default=DeliveryMethod.WEBSOCKET)
    retry_count: int = SQLField(default=0)
    error_message: Optional[str] = SQLField(default=None)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)


# T14: UserProfile Model
class UserProfile(SQLModel, table=True):
    """Stores user-specific preferences for advanced features.

    Attributes:
        id: Unique identifier for the profile
        user_id: User this profile belongs to
        default_priority: Default priority for new tasks
        default_reminder_offset_minutes: Default reminder time before due date
        default_tags: Suggested tags for the user
        notification_preferences: Delivery method preferences
        timezone: User's timezone for due date calculations
    """
    __tablename__ = "user_profiles"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    user_id: UUID = SQLField(unique=True, index=True)
    default_priority: Optional[Priority] = SQLField(default=None)
    default_reminder_offset_minutes: int = SQLField(default=60)
    default_tags: List[str] = SQLField(default_factory=list, sa_column=Column(JSON))
    notification_preferences: Dict[str, Any] = SQLField(default_factory=dict, sa_column=Column(JSON))
    timezone: str = SQLField(default="UTC")
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)


# T015: RecurringRule Model
class RecurringRule(SQLModel, table=True):
    """Stores parsed recurrence metadata for efficient querying and display.

    Attributes:
        id: Unique identifier for the rule
        task_id: Task this rule applies to
        rrule_string: Full RFC 5545 RRule string
        frequency: Recurrence frequency (daily, weekly, monthly, yearly)
        interval: Every N periods
        by_day: Days of week for weekly recurrence
        by_month_day: Days of month for monthly recurrence
        count: Total occurrences (null for infinite)
        until: End date for recurrence
    """
    __tablename__ = "recurring_rules"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    task_id: UUID = SQLField(unique=True, index=True)
    rrule_string: str
    frequency: RecurrenceFrequency
    interval: int = SQLField(default=1)
    by_day: Optional[List[str]] = SQLField(default=None, sa_column=Column(JSON))
    by_month_day: Optional[List[int]] = SQLField(default=None, sa_column=Column(JSON))
    count: Optional[int] = SQLField(default=None)
    until: Optional[datetime] = SQLField(default=None)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)


# Pydantic schemas for API requests/responses

class TaskEventCreate(BaseModel):
    """Schema for creating a task event."""
    event_type: str
    user_id: UUID
    task_id: UUID
    data: Dict[str, Any] = Field(default_factory=dict)


class TaskEventResponse(BaseModel):
    """Schema for task event API response."""
    id: UUID
    event_type: str
    schema_version: str
    timestamp: datetime
    user_id: UUID
    task_id: UUID
    data: Dict[str, Any]

    class Config:
        from_attributes = True


class ReminderCreate(BaseModel):
    """Schema for creating a reminder."""
    task_id: UUID
    user_id: UUID
    scheduled_time: datetime
    delivery_method: DeliveryMethod = DeliveryMethod.WEBSOCKET


class ReminderResponse(BaseModel):
    """Schema for reminder API response."""
    id: UUID
    task_id: UUID
    user_id: UUID
    scheduled_time: datetime
    sent_at: Optional[datetime]
    status: ReminderStatus
    delivery_method: DeliveryMethod
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    default_priority: Optional[Priority] = None
    default_reminder_offset_minutes: Optional[int] = None
    default_tags: Optional[List[str]] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None


class UserProfileResponse(BaseModel):
    """Schema for user profile API response."""
    id: UUID
    user_id: UUID
    default_priority: Optional[Priority]
    default_reminder_offset_minutes: int
    default_tags: List[str]
    notification_preferences: Dict[str, Any]
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecurringRuleCreate(BaseModel):
    """Schema for creating a recurring rule."""
    task_id: UUID
    rrule_string: str
    frequency: RecurrenceFrequency
    interval: int = 1
    by_day: Optional[List[str]] = None
    by_month_day: Optional[List[int]] = None
    count: Optional[int] = None
    until: Optional[datetime] = None


class RecurringRuleResponse(BaseModel):
    """Schema for recurring rule API response."""
    id: UUID
    task_id: UUID
    rrule_string: str
    frequency: RecurrenceFrequency
    interval: int
    by_day: Optional[List[str]]
    by_month_day: Optional[List[int]]
    count: Optional[int]
    until: Optional[datetime]

    class Config:
        from_attributes = True
