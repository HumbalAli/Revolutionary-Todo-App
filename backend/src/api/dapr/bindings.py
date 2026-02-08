"""Dapr bindings handler for scheduled operations.

This module provides FastAPI endpoints for Dapr input bindings,
including cron triggers for reminder checks and recurring tasks.

Phase V Integration:
- Reminder service for due reminders
- Recurring service for task recurrence
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Request, Response, Depends
from sqlalchemy.orm import Session

from ...database import get_session
from ...services.reminder_service import get_reminder_service
from ...services.recurring_service import get_recurring_service
from ...services.kafka_service import get_kafka_service
from ...models.todo_models import Task, TaskStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dapr/bindings", tags=["dapr-bindings"])


@router.post("/reminder-cron")
async def handle_reminder_cron(request: Request) -> Response:
    """Handle cron trigger for reminder checks.

    This endpoint is called by Dapr's cron binding every minute
    to check for tasks with approaching due dates and publish
    reminder events.

    Args:
        request: FastAPI request from Dapr

    Returns:
        Response with status
    """
    try:
        logger.info("Reminder cron triggered")

        # Get request data (Dapr sends binding metadata)
        try:
            data = await request.json()
        except Exception:
            data = {}

        # Run reminder check using reminder service
        await _check_due_reminders()

        return Response(status_code=200, content='{"status": "SUCCESS"}')

    except Exception as e:
        logger.error(f"Error in reminder cron handler: {e}")
        return Response(status_code=500, content='{"status": "ERROR"}')


async def _check_due_reminders() -> None:
    """Check for tasks with approaching due dates and publish reminder events.

    This function uses the ReminderService to:
    1. Query for due reminders
    2. Publish reminder events to Kafka
    3. Update reminder status
    """
    from ...database import SessionLocal

    logger.info("Checking for due reminders...")

    session = SessionLocal()
    try:
        reminder_service = get_reminder_service()
        kafka_service = get_kafka_service()

        # Process all due reminders
        stats = await reminder_service.process_due_reminders(session)

        logger.info(
            f"Reminder check completed - Processed: {stats['processed']}, "
            f"Sent: {stats['sent']}, Failed: {stats['failed']}"
        )

        # Also check for tasks nearing due date without reminders
        now = datetime.utcnow()
        window_end = now + timedelta(hours=24)

        tasks_needing_reminders = session.query(Task).filter(
            Task.due_date >= now,
            Task.due_date <= window_end,
            Task.completed == False,
            Task.status != TaskStatus.COMPLETED,
            Task.reminder_offset_minutes.isnot(None)
        ).all()

        for task in tasks_needing_reminders:
            # Check if reminder already exists
            existing = await reminder_service.get_pending_reminders_for_task(session, task.id)
            if not existing and task.due_date:
                # Create reminder for this task
                await reminder_service.create_reminder(
                    session=session,
                    task_id=task.id,
                    user_id=task.user_id,
                    due_date=task.due_date,
                    offset_minutes=task.reminder_offset_minutes or 60
                )
                logger.info(f"Created reminder for task {task.id}")

    except Exception as e:
        logger.error(f"Error processing reminders: {e}")
    finally:
        session.close()


@router.post("/recurring-task-cron")
async def handle_recurring_task_cron(request: Request) -> Response:
    """Handle cron trigger for recurring task management.

    This endpoint handles:
    1. Cleanup of old completed occurrences
    2. Verification of recurring rule integrity
    3. Pre-generation of upcoming recurring tasks

    Args:
        request: FastAPI request from Dapr

    Returns:
        Response with status
    """
    try:
        logger.info("Recurring task cron triggered")

        # Run recurring task maintenance
        await _process_recurring_tasks()

        return Response(status_code=200, content='{"status": "SUCCESS"}')

    except Exception as e:
        logger.error(f"Error in recurring task cron handler: {e}")
        return Response(status_code=500, content='{"status": "ERROR"}')


async def _process_recurring_tasks() -> None:
    """Process recurring task maintenance.

    This function handles:
    1. Cleanup of old completed occurrences (older than 30 days)
    2. Verification of recurring rule integrity
    3. Pre-generation of next occurrences for soon-due recurring tasks
    """
    from ...database import SessionLocal

    logger.info("Processing recurring tasks...")

    session = SessionLocal()
    try:
        recurring_service = get_recurring_service()
        kafka_service = get_kafka_service()

        # Get all active recurring tasks
        recurring_tasks = session.query(Task).filter(
            Task.is_recurring == True,
            Task.completed == False,
            Task.recurrence_rule.isnot(None)
        ).all()

        stats = {"validated": 0, "invalid": 0, "cleaned": 0}

        for task in recurring_tasks:
            # Validate the recurrence rule
            if recurring_service.validate_rrule(task.recurrence_rule):
                stats["validated"] += 1

                # Get next occurrence info
                next_occurrence = recurring_service.get_next_occurrence(
                    task.recurrence_rule,
                    datetime.utcnow()
                )

                if next_occurrence:
                    logger.debug(f"Task {task.id} next occurrence: {next_occurrence}")
            else:
                stats["invalid"] += 1
                logger.warning(f"Task {task.id} has invalid recurrence rule: {task.recurrence_rule}")

        # Clean up old completed recurring task occurrences
        retention_days = 30
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        old_occurrences = session.query(Task).filter(
            Task.recurrence_parent_id.isnot(None),
            Task.completed == True,
            Task.updated_at < cutoff_date
        ).all()

        if old_occurrences:
            for old_task in old_occurrences:
                # Log for audit before deletion
                logger.info(f"Cleaning up old recurring occurrence: Task {old_task.id}")
                session.delete(old_task)
                stats["cleaned"] += 1

            session.commit()

        logger.info(
            f"Recurring task processing completed - Validated: {stats['validated']}, "
            f"Invalid: {stats['invalid']}, Cleaned: {stats['cleaned']}"
        )

    except Exception as e:
        logger.error(f"Error processing recurring tasks: {e}")
        session.rollback()
    finally:
        session.close()


@router.options("/reminder-cron")
async def reminder_cron_options() -> Response:
    """Handle OPTIONS request for reminder-cron binding.

    Returns:
        Response with allowed methods
    """
    return Response(
        status_code=200,
        headers={
            "Allow": "POST, OPTIONS",
            "Accept": "application/json"
        }
    )


@router.options("/recurring-task-cron")
async def recurring_task_cron_options() -> Response:
    """Handle OPTIONS request for recurring-task-cron binding.

    Returns:
        Response with allowed methods
    """
    return Response(
        status_code=200,
        headers={
            "Allow": "POST, OPTIONS",
            "Accept": "application/json"
        }
    )
