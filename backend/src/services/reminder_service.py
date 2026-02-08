"""Reminder service for scheduling and managing task notifications.

This module provides functionality for:
- Creating reminders for tasks with due dates
- Checking for due reminders
- Publishing reminder events to Kafka
- Updating reminder status after delivery
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..models.todo_models import Task, TaskStatus
from ..models.event_models import (
    Reminder, 
    ReminderStatus, 
    DeliveryMethod,
    ReminderCreate,
    ReminderResponse
)
from .kafka_service import get_kafka_service

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for managing task reminders.
    
    This service handles:
    - Creating reminders when tasks with due dates are created
    - Querying for due reminders
    - Updating reminder status after delivery
    - Publishing reminder events to Kafka
    """

    async def create_reminder(
        self,
        session: Session,
        task_id: int,
        user_id: int,
        due_date: datetime,
        offset_minutes: int = 60,
        delivery_method: DeliveryMethod = DeliveryMethod.WEBSOCKET
    ) -> Optional[Reminder]:
        """Create a reminder for a task.
        
        Args:
            session: Database session
            task_id: ID of the task
            user_id: ID of the user to notify
            due_date: When the task is due
            offset_minutes: Minutes before due date to send reminder
            delivery_method: How to deliver the reminder
            
        Returns:
            Created Reminder object or None if creation failed
        """
        try:
            scheduled_time = due_date - timedelta(minutes=offset_minutes)
            
            # Don't create reminders for past times
            if scheduled_time <= datetime.utcnow():
                logger.info(f"Skipping reminder for task {task_id} - scheduled time is in the past")
                return None
            
            reminder = Reminder(
                id=uuid4(),
                task_id=UUID(str(task_id)) if isinstance(task_id, int) else task_id,
                user_id=UUID(str(user_id)) if isinstance(user_id, int) else user_id,
                scheduled_time=scheduled_time,
                status=ReminderStatus.PENDING,
                delivery_method=delivery_method,
                retry_count=0
            )
            
            session.add(reminder)
            session.commit()
            session.refresh(reminder)
            
            logger.info(f"Created reminder for task {task_id} at {scheduled_time}")
            return reminder
            
        except Exception as e:
            logger.error(f"Failed to create reminder for task {task_id}: {e}")
            session.rollback()
            return None

    async def get_due_reminders(
        self,
        session: Session,
        window_minutes: int = 5
    ) -> List[Reminder]:
        """Get reminders that are due within the specified window.
        
        Args:
            session: Database session
            window_minutes: Time window in minutes to check for due reminders
            
        Returns:
            List of due reminders
        """
        now = datetime.utcnow()
        window_end = now + timedelta(minutes=window_minutes)
        
        reminders = session.query(Reminder).filter(
            Reminder.status == ReminderStatus.PENDING,
            Reminder.scheduled_time >= now,
            Reminder.scheduled_time <= window_end
        ).all()
        
        logger.info(f"Found {len(reminders)} due reminders in the next {window_minutes} minutes")
        return reminders

    async def get_pending_reminders_for_task(
        self,
        session: Session,
        task_id: int
    ) -> List[Reminder]:
        """Get all pending reminders for a specific task.
        
        Args:
            session: Database session
            task_id: ID of the task
            
        Returns:
            List of pending reminders
        """
        task_uuid = UUID(str(task_id)) if isinstance(task_id, int) else task_id
        
        return session.query(Reminder).filter(
            Reminder.task_id == task_uuid,
            Reminder.status == ReminderStatus.PENDING
        ).all()

    async def mark_reminder_sent(
        self,
        session: Session,
        reminder_id: UUID
    ) -> bool:
        """Mark a reminder as sent.
        
        Args:
            session: Database session
            reminder_id: ID of the reminder
            
        Returns:
            True if update succeeded
        """
        try:
            reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not reminder:
                logger.warning(f"Reminder {reminder_id} not found")
                return False
            
            reminder.status = ReminderStatus.SENT
            reminder.sent_at = datetime.utcnow()
            reminder.updated_at = datetime.utcnow()
            
            session.commit()
            logger.info(f"Marked reminder {reminder_id} as sent")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark reminder {reminder_id} as sent: {e}")
            session.rollback()
            return False

    async def mark_reminder_failed(
        self,
        session: Session,
        reminder_id: UUID,
        error_message: str
    ) -> bool:
        """Mark a reminder as failed with error details.
        
        Args:
            session: Database session
            reminder_id: ID of the reminder
            error_message: Error details
            
        Returns:
            True if update succeeded
        """
        try:
            reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not reminder:
                logger.warning(f"Reminder {reminder_id} not found")
                return False
            
            reminder.retry_count += 1
            reminder.error_message = error_message
            reminder.updated_at = datetime.utcnow()
            
            # Mark as failed if max retries exceeded
            if reminder.retry_count >= 3:
                reminder.status = ReminderStatus.FAILED
                logger.warning(f"Reminder {reminder_id} marked as failed after {reminder.retry_count} retries")
            
            session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update reminder {reminder_id}: {e}")
            session.rollback()
            return False

    async def cancel_task_reminders(
        self,
        session: Session,
        task_id: int
    ) -> int:
        """Cancel all pending reminders for a task.
        
        Args:
            session: Database session
            task_id: ID of the task
            
        Returns:
            Number of reminders cancelled
        """
        try:
            task_uuid = UUID(str(task_id)) if isinstance(task_id, int) else task_id
            
            count = session.query(Reminder).filter(
                Reminder.task_id == task_uuid,
                Reminder.status == ReminderStatus.PENDING
            ).update({
                "status": ReminderStatus.CANCELLED,
                "updated_at": datetime.utcnow()
            })
            
            session.commit()
            logger.info(f"Cancelled {count} reminders for task {task_id}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cancel reminders for task {task_id}: {e}")
            session.rollback()
            return 0

    async def process_due_reminders(
        self,
        session: Session
    ) -> Dict[str, int]:
        """Process all due reminders and publish to Kafka.
        
        This is called by the Dapr cron binding.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with processing statistics
        """
        stats = {"processed": 0, "sent": 0, "failed": 0}
        
        reminders = await self.get_due_reminders(session)
        kafka_service = get_kafka_service()
        
        for reminder in reminders:
            stats["processed"] += 1
            
            try:
                # Get the associated task
                task = session.query(Task).filter(
                    Task.id == int(str(reminder.task_id))
                ).first()
                
                if not task:
                    logger.warning(f"Task not found for reminder {reminder.id}")
                    continue
                
                # Skip completed tasks
                if task.completed or task.status == TaskStatus.COMPLETED:
                    await self.cancel_task_reminders(session, task.id)
                    continue
                
                # Publish reminder.due event
                success = await kafka_service.publish_reminder_due(
                    user_id=reminder.user_id,
                    task_id=reminder.task_id,
                    reminder_id=reminder.id,
                    task_title=task.title,
                    due_date=task.due_date,
                    scheduled_time=reminder.scheduled_time,
                    delivery_method=reminder.delivery_method.value,
                    priority=task.priority.value if task.priority else None
                )
                
                if success:
                    await self.mark_reminder_sent(session, reminder.id)
                    stats["sent"] += 1
                    
                    # Publish reminder.sent confirmation
                    await kafka_service.publish_reminder_sent(
                        user_id=reminder.user_id,
                        task_id=reminder.task_id,
                        reminder_id=reminder.id,
                        delivery_method=reminder.delivery_method.value,
                        retry_count=reminder.retry_count
                    )
                else:
                    await self.mark_reminder_failed(
                        session, 
                        reminder.id, 
                        "Failed to publish to Kafka"
                    )
                    stats["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing reminder {reminder.id}: {e}")
                await self.mark_reminder_failed(session, reminder.id, str(e))
                stats["failed"] += 1
        
        logger.info(f"Processed {stats['processed']} reminders: {stats['sent']} sent, {stats['failed']} failed")
        return stats

    async def reschedule_reminder(
        self,
        session: Session,
        task_id: int,
        new_due_date: datetime,
        offset_minutes: int = 60
    ) -> Optional[Reminder]:
        """Reschedule reminders when a task's due date changes.
        
        Args:
            session: Database session
            task_id: ID of the task
            new_due_date: New due date
            offset_minutes: Minutes before due date to send reminder
            
        Returns:
            New reminder or None
        """
        # Cancel existing pending reminders
        await self.cancel_task_reminders(session, task_id)
        
        # Get task details
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # Create new reminder
        return await self.create_reminder(
            session=session,
            task_id=task_id,
            user_id=task.user_id,
            due_date=new_due_date,
            offset_minutes=offset_minutes
        )


# Global reminder service instance
reminder_service = ReminderService()


def get_reminder_service() -> ReminderService:
    """Get the global reminder service instance.
    
    Returns:
        ReminderService instance
    """
    return reminder_service
