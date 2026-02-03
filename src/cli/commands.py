"""Command handlers for CLI interface.

This module provides command implementations for all user actions.
"""

from typing import Optional
from services.storage import (
    get_all_tasks,
    add_task,
    get_task,
    update_task,
    delete_task,
    toggle_complete,
)
from cli.display import (
    display_tasks,
    display_success_message,
    display_error_message,
    display_status_toggle,
)


def get_user_input(prompt: str) -> str:
    """Get user input from console.

    Args:
        prompt: Prompt message to display

    Returns:
        User's input as string
    """
    return input(prompt).strip()


def validate_title(title: str) -> bool:
    """Validate task title.

    Args:
        title: Title to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(title and title.strip())


def add_task_command() -> None:
    """Handle the add task command."""
    print("\n--- Add Task ---")

    title = get_user_input("Enter task title: ")
    if not validate_title(title):
        display_error_message("Task title cannot be empty.")
        return

    description = get_user_input("Enter task description (optional): ")

    task = add_task(title, description)
    display_success_message(f"Task added: '{task.title}' (ID: {task.id})")


def view_tasks_command() -> None:
    """Handle the view tasks command."""
    print("\n--- View Tasks ---")
    tasks = get_all_tasks()
    display_tasks(tasks)


def mark_complete_command() -> None:
    """Handle the mark task complete command."""
    print("\n--- Mark Task Complete ---")

    task_id_input = get_user_input("Enter task ID: ")
    try:
        task_id = int(task_id_input)
    except ValueError:
        display_error_message("Invalid task ID. Please enter a number.")
        return

    task = toggle_complete(task_id)
    if task:
        display_status_toggle(task)
    else:
        display_error_message(f"Task with ID {task_id} not found.")


def update_task_command() -> None:
    """Handle the update task command."""
    print("\n--- Update Task ---")

    task_id_input = get_user_input("Enter task ID to update: ")
    try:
        task_id = int(task_id_input)
    except ValueError:
        display_error_message("Invalid task ID. Please enter a number.")
        return

    task = get_task(task_id)
    if not task:
        display_error_message(f"Task with ID {task_id} not found.")
        return

    print(f"\nCurrent task:")
    print(f"  Title: {task.title}")
    print(f"  Description: {task.description}")

    title = get_user_input("\nEnter new title (leave blank to keep current): ")
    description = get_user_input("Enter new description (leave blank to keep current): ")

    if not title:
        title = None
    if not description:
        description = None

    updated_task = update_task(task_id, title, description)
    if updated_task:
        display_success_message(f"Task updated: '{updated_task.title}' (ID: {updated_task.id})")
    else:
        display_error_message("Failed to update task.")


def delete_task_command() -> None:
    """Handle the delete task command."""
    print("\n--- Delete Task ---")

    task_id_input = get_user_input("Enter task ID to delete: ")
    try:
        task_id = int(task_id_input)
    except ValueError:
        display_error_message("Invalid task ID. Please enter a number.")
        return

    task = get_task(task_id)
    if not task:
        display_error_message(f"Task with ID {task_id} not found.")
        return

    print(f"\nTask to delete: '{task.title}' (ID: {task.id})")
    confirm = get_user_input("Are you sure? (y/n): ").lower()

    if confirm == "y":
        if delete_task(task_id):
            display_success_message(f"Task deleted: '{task.title}'")
        else:
            display_error_message("Failed to delete task.")
    else:
        print("\nDeletion cancelled.")


def exit_command() -> None:
    """Handle the exit command."""
    print("\nGoodbye!")


def handle_invalid_input() -> None:
    """Handle invalid user input."""
    display_error_message("Invalid input. Please try again.")
