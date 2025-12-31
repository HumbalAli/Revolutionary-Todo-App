"""Menu handling for CLI interface.

This module provides main menu display and routing.
"""

from cli.display import display_menu
from cli.commands import (
    view_tasks_command,
    add_task_command,
    mark_complete_command,
    update_task_command,
    delete_task_command,
    exit_command,
)


def get_user_choice() -> str:
    """Get user's menu choice.

    Returns:
        User's choice as string
    """
    return input("Enter your choice (1-6): ").strip()


def main_menu() -> None:
    """Main application menu loop."""
    while True:
        display_menu()
        choice = get_user_choice()

        if choice == "1":
            view_tasks_command()
        elif choice == "2":
            add_task_command()
        elif choice == "3":
            mark_complete_command()
        elif choice == "4":
            update_task_command()
        elif choice == "5":
            delete_task_command()
        elif choice == "6":
            exit_command()
            break
        else:
            print("\n[ERROR] Invalid choice. Please enter a number between 1 and 6.")
