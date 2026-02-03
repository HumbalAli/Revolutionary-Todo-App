"""CLI interface for Todo application."""

from .display import (
    display_tasks,
    display_empty_message,
    display_menu,
    display_success_message,
    display_error_message,
    display_status_toggle,
)
from .menu import main_menu, get_user_choice
from .commands import (
    add_task_command,
    view_tasks_command,
    mark_complete_command,
    update_task_command,
    delete_task_command,
    exit_command,
    handle_invalid_input,
)

__all__ = [
    "display_tasks",
    "display_empty_message",
    "display_menu",
    "display_success_message",
    "display_error_message",
    "display_status_toggle",
    "main_menu",
    "get_user_choice",
    "add_task_command",
    "view_tasks_command",
    "mark_complete_command",
    "update_task_command",
    "delete_task_command",
    "exit_command",
    "handle_invalid_input",
]
