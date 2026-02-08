"""Recurring task service for handling RRule-based recurrence patterns.

This module provides functionality for parsing RFC 5545 RRule strings
and generating next occurrence dates for recurring tasks.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dateutil.rrule import rrulestr, rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.relativedelta import relativedelta

from ..models.todo_models import Task, TaskCreate, Priority, TaskStatus
from ..models.event_models import RecurringRule, RecurrenceFrequency

logger = logging.getLogger(__name__)


# Frequency mapping from RRule to enum
FREQUENCY_MAP = {
    DAILY: RecurrenceFrequency.DAILY,
    WEEKLY: RecurrenceFrequency.WEEKLY,
    MONTHLY: RecurrenceFrequency.MONTHLY,
    YEARLY: RecurrenceFrequency.YEARLY
}


class RecurringTaskService:
    """Service for managing recurring task patterns.

    This service handles:
    - Parsing RRule strings into structured data
    - Generating next occurrence dates
    - Creating new task instances for recurring tasks
    """

    def parse_rrule(self, rrule_string: str) -> Optional[Dict[str, Any]]:
        """Parse an RRule string into structured data.

        Args:
            rrule_string: RFC 5545 RRule string (e.g., "FREQ=WEEKLY;BYDAY=MO,WE,FR")

        Returns:
            Dictionary with parsed rule components or None if invalid
        """
        try:
            # Parse the RRule string
            rule = rrulestr(rrule_string)

            # Extract components
            parsed = {
                "rrule_string": rrule_string,
                "frequency": FREQUENCY_MAP.get(rule._freq, RecurrenceFrequency.DAILY),
                "interval": rule._interval or 1,
                "by_day": None,
                "by_month_day": None,
                "count": rule._count,
                "until": rule._until
            }

            # Extract byweekday if present
            if rule._byweekday:
                day_names = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
                parsed["by_day"] = [day_names[d] for d in rule._byweekday]

            # Extract bymonthday if present
            if rule._bymonthday:
                parsed["by_month_day"] = list(rule._bymonthday)

            return parsed

        except Exception as e:
            logger.error(f"Failed to parse RRule string: {rrule_string}, error: {e}")
            return None

    def get_next_occurrence(
        self,
        rrule_string: str,
        current_date: datetime,
        occurrence_count: int = 1
    ) -> Optional[datetime]:
        """Calculate the next occurrence date based on RRule.

        Args:
            rrule_string: RFC 5545 RRule string
            current_date: Current task's due date (or completion date)
            occurrence_count: Current occurrence number

        Returns:
            Next occurrence datetime or None if no more occurrences
        """
        try:
            # Parse the RRule with the current date as dtstart
            rule = rrulestr(rrule_string, dtstart=current_date)

            # Get all occurrences after current_date
            next_dates = list(rule.after(current_date, inc=False, count=1))

            if next_dates:
                return next_dates[0]

            return None

        except Exception as e:
            logger.error(f"Failed to calculate next occurrence: {e}")
            return None

    def generate_next_occurrence(
        self,
        task: Task,
        completed_at: Optional[datetime] = None
    ) -> Optional[TaskCreate]:
        """Generate the next occurrence for a recurring task.

        Args:
            task: The completed recurring task
            completed_at: When the task was completed (defaults to now)

        Returns:
            TaskCreate schema for the next occurrence or None
        """
        if not task.is_recurring or not task.recurrence_rule:
            logger.warning(f"Task {task.id} is not a recurring task")
            return None

        # Use current due_date or completion time as reference
        reference_date = task.due_date or completed_at or datetime.utcnow()

        # Calculate next occurrence
        next_date = self.get_next_occurrence(
            task.recurrence_rule,
            reference_date,
            task.recurrence_count or 1
        )

        if not next_date:
            logger.info(f"No more occurrences for task {task.id}")
            return None

        # Create the next occurrence
        next_occurrence = TaskCreate(
            title=task.title,
            description=task.description,
            due_date=next_date,
            priority=task.priority,
            tags=task.tags.copy() if task.tags else [],
            recurrence_rule=task.recurrence_rule,
            reminder_offset_minutes=task.reminder_offset_minutes
        )

        logger.info(f"Generated next occurrence for task {task.id}: due {next_date}")
        return next_occurrence

    def create_recurring_rule(
        self,
        task_id: int,
        rrule_string: str
    ) -> Optional[RecurringRule]:
        """Create a RecurringRule entity from an RRule string.

        Args:
            task_id: ID of the task this rule applies to
            rrule_string: RFC 5545 RRule string

        Returns:
            RecurringRule entity or None if parsing fails
        """
        parsed = self.parse_rrule(rrule_string)
        if not parsed:
            return None

        return RecurringRule(
            task_id=task_id,
            rrule_string=rrule_string,
            frequency=parsed["frequency"],
            interval=parsed["interval"],
            by_day=parsed["by_day"],
            by_month_day=parsed["by_month_day"],
            count=parsed["count"],
            until=parsed["until"]
        )

    def validate_rrule(self, rrule_string: str) -> bool:
        """Validate an RRule string.

        Args:
            rrule_string: RFC 5545 RRule string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            rrulestr(rrule_string)
            return True
        except Exception:
            return False

    def get_rrule_presets(self) -> Dict[str, str]:
        """Get common RRule presets for UI.

        Returns:
            Dictionary of preset names to RRule strings
        """
        return {
            "daily": "FREQ=DAILY",
            "weekdays": "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
            "weekly": "FREQ=WEEKLY",
            "biweekly": "FREQ=WEEKLY;INTERVAL=2",
            "monthly": "FREQ=MONTHLY",
            "monthly_first_monday": "FREQ=MONTHLY;BYDAY=1MO",
            "quarterly": "FREQ=MONTHLY;INTERVAL=3",
            "yearly": "FREQ=YEARLY"
        }

    def describe_rrule(self, rrule_string: str) -> str:
        """Generate a human-readable description of an RRule.

        Args:
            rrule_string: RFC 5545 RRule string

        Returns:
            Human-readable description
        """
        parsed = self.parse_rrule(rrule_string)
        if not parsed:
            return "Invalid recurrence rule"

        freq = parsed["frequency"].value.lower()
        interval = parsed["interval"]

        # Build description
        if interval == 1:
            desc = f"Repeats {freq}"
        else:
            desc = f"Repeats every {interval} {freq}s"

        # Add day specification for weekly
        if parsed["by_day"]:
            days = ", ".join(parsed["by_day"])
            desc += f" on {days}"

        # Add day specification for monthly
        if parsed["by_month_day"]:
            days = ", ".join(str(d) for d in parsed["by_month_day"])
            desc += f" on day(s) {days}"

        # Add count/until
        if parsed["count"]:
            desc += f", {parsed['count']} times"
        elif parsed["until"]:
            desc += f", until {parsed['until'].strftime('%Y-%m-%d')}"

        return desc


# Global service instance
recurring_service = RecurringTaskService()


def get_recurring_service() -> RecurringTaskService:
    """Get the global recurring task service instance.

    Returns:
        RecurringTaskService instance
    """
    return recurring_service
