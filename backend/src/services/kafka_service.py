"""Kafka service for event-driven architecture.

This module provides the base Kafka producer/consumer functionality
for publishing and consuming events from Kafka topics.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable, List
from uuid import UUID

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class KafkaEvent(BaseModel):
    """Base schema for Kafka events."""
    event_type: str
    schema_version: str = "1.0"
    timestamp: datetime
    user_id: UUID
    task_id: UUID
    data: Dict[str, Any]


class KafkaService:
    """Kafka service for publishing and consuming events.

    This service abstracts Kafka operations and integrates with Dapr pub/sub
    for cloud-native event handling.

    Attributes:
        brokers: Kafka broker addresses
        pubsub_name: Dapr pub/sub component name
        dapr_port: Dapr sidecar HTTP port
    """

    def __init__(
        self,
        brokers: str = "localhost:9092",
        pubsub_name: str = "kafka-pubsub",
        dapr_port: int = 3500
    ):
        """Initialize Kafka service.

        Args:
            brokers: Kafka broker addresses (comma-separated)
            pubsub_name: Name of the Dapr pub/sub component
            dapr_port: Dapr sidecar HTTP port
        """
        self.brokers = brokers
        self.pubsub_name = pubsub_name
        self.dapr_port = dapr_port
        self._producer = None
        self._consumers: Dict[str, Any] = {}

    async def publish_event(
        self,
        topic: str,
        event: KafkaEvent,
        key: Optional[str] = None
    ) -> bool:
        """Publish an event to a Kafka topic via Dapr pub/sub.

        Args:
            topic: Kafka topic name
            event: Event data to publish
            key: Optional partition key (defaults to user_id)

        Returns:
            True if publish succeeded, False otherwise
        """
        import httpx

        try:
            # Serialize event data
            event_data = event.model_dump(mode='json')

            # Use Dapr pub/sub API
            dapr_url = f"http://localhost:{self.dapr_port}/v1.0/publish/{self.pubsub_name}/{topic}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    dapr_url,
                    json=event_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 204):
                    logger.info(f"Published event to {topic}: {event.event_type}")
                    return True
                else:
                    logger.error(f"Failed to publish event: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Error publishing event to {topic}: {e}")
            return False

    async def publish_task_created(
        self,
        user_id: UUID,
        task_id: UUID,
        task_data: Dict[str, Any]
    ) -> bool:
        """Publish a task.created event.

        Args:
            user_id: ID of the user who created the task
            task_id: ID of the created task
            task_data: Task properties

        Returns:
            True if publish succeeded
        """
        event = KafkaEvent(
            event_type="task.created",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            task_id=task_id,
            data=task_data
        )
        return await self.publish_event("task-events", event, key=str(user_id))

    async def publish_task_updated(
        self,
        user_id: UUID,
        task_id: UUID,
        changes: Dict[str, Any]
    ) -> bool:
        """Publish a task.updated event.

        Args:
            user_id: ID of the user who updated the task
            task_id: ID of the updated task
            changes: Changed properties with old/new values

        Returns:
            True if publish succeeded
        """
        event = KafkaEvent(
            event_type="task.updated",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            task_id=task_id,
            data={"changes": changes}
        )
        return await self.publish_event("task-events", event, key=str(user_id))

    async def publish_task_completed(
        self,
        user_id: UUID,
        task_id: UUID,
        is_recurring: bool = False,
        next_occurrence_id: Optional[UUID] = None
    ) -> bool:
        """Publish a task.completed event.

        Args:
            user_id: ID of the user who completed the task
            task_id: ID of the completed task
            is_recurring: Whether this was a recurring task
            next_occurrence_id: ID of the next occurrence if recurring

        Returns:
            True if publish succeeded
        """
        event = KafkaEvent(
            event_type="task.completed",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            task_id=task_id,
            data={
                "completed_at": datetime.utcnow().isoformat(),
                "is_recurring": is_recurring,
                "next_occurrence_id": str(next_occurrence_id) if next_occurrence_id else None
            }
        )
        return await self.publish_event("task-events", event, key=str(user_id))

    async def publish_task_deleted(
        self,
        user_id: UUID,
        task_id: UUID,
        reason: Optional[str] = None
    ) -> bool:
        """Publish a task.deleted event.

        Args:
            user_id: ID of the user who deleted the task
            task_id: ID of the deleted task
            reason: Optional reason for deletion

        Returns:
            True if publish succeeded
        """
        event = KafkaEvent(
            event_type="task.deleted",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            task_id=task_id,
            data={
                "deleted_at": datetime.utcnow().isoformat(),
                "reason": reason
            }
        )
        return await self.publish_event("task-events", event, key=str(user_id))

    async def publish_reminder_due(
        self,
        user_id: UUID,
        task_id: UUID,
        reminder_id: UUID,
        task_title: str,
        due_date: datetime,
        scheduled_time: datetime,
        delivery_method: str = "WEBSOCKET",
        priority: Optional[str] = None
    ) -> bool:
        """Publish a reminder.due event.

        Args:
            user_id: ID of the user to notify
            task_id: ID of the task
            reminder_id: ID of the reminder
            task_title: Title of the task
            due_date: When the task is due
            scheduled_time: When the reminder should be sent
            delivery_method: How to deliver the reminder
            priority: Task priority

        Returns:
            True if publish succeeded
        """
        event = KafkaEvent(
            event_type="reminder.due",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            task_id=task_id,
            data={
                "reminder_id": str(reminder_id),
                "task_title": task_title,
                "due_date": due_date.isoformat(),
                "scheduled_time": scheduled_time.isoformat(),
                "delivery_method": delivery_method,
                "priority": priority
            }
        )
        return await self.publish_event("reminders", event, key=str(user_id))

    async def publish_reminder_sent(
        self,
        user_id: UUID,
        task_id: UUID,
        reminder_id: UUID,
        delivery_method: str,
        retry_count: int = 0
    ) -> bool:
        """Publish a reminder.sent event.

        Args:
            user_id: ID of the user notified
            task_id: ID of the task
            reminder_id: ID of the reminder
            delivery_method: How the reminder was delivered
            retry_count: Number of delivery attempts

        Returns:
            True if publish succeeded
        """
        event = KafkaEvent(
            event_type="reminder.sent",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            task_id=task_id,
            data={
                "reminder_id": str(reminder_id),
                "sent_at": datetime.utcnow().isoformat(),
                "delivery_method": delivery_method,
                "retry_count": retry_count
            }
        )
        return await self.publish_event("reminders", event, key=str(user_id))

    async def publish_task_priority_changed(
        self,
        user_id: UUID,
        task_id: UUID,
        old_priority: str,
        new_priority: str
    ) -> bool:
        """Publish a task.priority_changed event for real-time sync.

        Args:
            user_id: ID of the user
            task_id: ID of the task
            old_priority: Previous priority
            new_priority: New priority

        Returns:
            True if publish succeeded
        """
        event = KafkaEvent(
            event_type="task.priority_changed",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            task_id=task_id,
            data={
                "old_priority": old_priority,
                "new_priority": new_priority
            }
        )
        return await self.publish_event("task-updates", event, key=str(user_id))

    async def publish_task_due_date_changed(
        self,
        user_id: UUID,
        task_id: UUID,
        old_due_date: Optional[datetime],
        new_due_date: Optional[datetime]
    ) -> bool:
        """Publish a task.due_date_changed event for real-time sync.

        Args:
            user_id: ID of the user
            task_id: ID of the task
            old_due_date: Previous due date
            new_due_date: New due date

        Returns:
            True if publish succeeded
        """
        event = KafkaEvent(
            event_type="task.due_date_changed",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            task_id=task_id,
            data={
                "old_due_date": old_due_date.isoformat() if old_due_date else None,
                "new_due_date": new_due_date.isoformat() if new_due_date else None
            }
        )
        return await self.publish_event("task-updates", event, key=str(user_id))

    async def close(self):
        """Close Kafka connections."""
        if self._producer:
            await self._producer.stop()
            self._producer = None

        for consumer in self._consumers.values():
            await consumer.stop()
        self._consumers.clear()


# Global Kafka service instance
kafka_service = KafkaService()


def get_kafka_service() -> KafkaService:
    """Get the global Kafka service instance.

    Returns:
        KafkaService instance
    """
    return kafka_service
