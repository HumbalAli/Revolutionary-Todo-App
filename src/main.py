"""Main entry point for the Todo Console Application."""

from cli.menu import main_menu


def main() -> None:
    """Run the Todo application."""
    print("Welcome to Todo App!")
    main_menu()


if __name__ == "__main__":
    main()
