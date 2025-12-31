# Todo Console App - Phase I

A simple in-memory Python console todo application with full CRUD functionality.

## Features

- View all tasks with completion status
- Add new tasks with title and optional description
- Mark tasks as complete/incomplete
- Update existing tasks
- Delete tasks
- Sequential task IDs (never re-used)

## Requirements

- Python 3.13+
- uv package manager

## Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .
```

## Usage

```bash
# Run the application
python src/main.py
```

## Menu Options

1. **View Tasks** - Display all tasks with their completion status
2. **Add Task** - Create a new task with title and optional description
3. **Mark Task Complete** - Toggle a task's completion status
4. **Update Task** - Modify an existing task's title and/or description
5. **Delete Task** - Permanently remove a task
6. **Exit** - Quit the application

## Example Workflow

```
=== Todo App ===
1. View Tasks
2. Add Task
3. Mark Task Complete
4. Update Task
5. Delete Task
6. Exit

Enter your choice (1-6): 2

--- Add Task ---
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread

✓ Task added: 'Buy groceries' (ID: 1)
```

## Project Structure

```
todo-app/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py           # Task dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── storage.py        # In-memory CRUD operations
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── display.py        # Formatted output
│   │   ├── menu.py           # Menu handling
│   │   └── commands.py       # Command implementations
│   └── main.py               # Entry point
├── tests/
├── specs/
└── README.md
```

## Performance

All operations complete in under 3 seconds per application requirements.

## Development

```bash
# Run tests
uv run pytest

# Run application
python src/main.py
```

## License

MIT
