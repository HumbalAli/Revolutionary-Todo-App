"""Display functions for CLI interface.

This module provides formatted output for tasks, messages, and menus.
"""

from typing import List
from models.task import Task


def format_task_table(tasks: List[Task]) -> str:
    """Format a list of tasks as a table.

    Args:
        tasks: List of tasks to format

    Returns:
        Formatted table string
    """
    if not tasks:
        return ""

    # Calculate column widths
    id_width = max(3, max(len(str(t.id)) for t in tasks))
    status_width = 8
    title_width = max(5, max(len(t.title) for t in tasks))
    desc_width = max(11, max(len(t.description) for t in tasks))

    # Create separator line
    separator = "-" * (id_width + status_width + title_width + desc_width + 9)

    # Format table
    lines = [
        separator,
        f"{'ID'.ljust(id_width)} | {'Status'.ljust(status_width)} | {'Title'.ljust(title_width)} | {'Description'.ljust(desc_width)}",
        separator,
    ]

    for task in tasks:
        status = "[x]" if task.completed else "[ ]"
        title_truncated = (task.title[:title_width - 3] + "...") if len(task.title) > title_width else task.title
        desc_truncated = (task.description[:desc_width - 3] + "...") if len(task.description) > desc_width else task.description

        lines.append(
            f"{str(task.id).ljust(id_width)} | {status.ljust(status_width)} | {title_truncated.ljust(title_width)} | {desc_truncated.ljust(desc_width)}"
        )

    lines.append(separator)
    return "\n".join(lines)


def display_tasks(tasks: List[Task]) -> None:
    """Display a list of tasks to the user.

    Args:
        tasks: List of tasks to display
    """
    if not tasks:
        display_empty_message()
    else:
        print("\n" + format_task_table(tasks))


def display_empty_message() -> None:
    """Display message when no tasks exist."""
    print("\nNo tasks found. Add a task to get started!")


def display_menu() -> None:
    """Display the main menu."""
    print("\n=== Todo App ===")
    print("1. View Tasks")
    print("2. Add Task")
    print("3. Mark Task Complete")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Exit")
    print()


def display_success_message(message: str) -> None:
    """Display a success message.

    Args:
        message: Success message to display
    """
    print(f"\n[OK] {message}")


def display_error_message(message: str) -> None:
    """Display an error message.

    Args:
        message: Error message to display
    """
    print(f"\n[ERROR] {message}")


def display_status_toggle(task: Task) -> None:
    """Display task status toggle message.

    Args:
        task: Task whose status was toggled
    """
    status = "completed" if task.completed else "incomplete"
    display_success_message(f"Task '{task.title}' marked as {status}.")
