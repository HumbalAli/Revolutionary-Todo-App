# Quickstart: Phase I - In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Date**: 2025-12-31

## Prerequisites

- Python 3.13 or higher
- uv package manager (for dependency management)
- Bash terminal or command prompt

## Installation

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Navigate to project directory:
   ```bash
   cd todo-app
   ```

3. Create virtual environment and install dependencies:
   ```bash
   uv venv
   uv pip install -e requirements.txt
   ```

4. Activate virtual environment:
   ```bash
   source .venv/bin/activate  # Linux/Mac
   .venv\Scriptsctivate       # Windows
   ```

## Running the Application

```bash
python src/main.py
```

## Expected Output

```
=== Todo App ====
1. Add Task
2. View Tasks
3. Update Task
4. Mark Complete
5. Delete Task
6. Exit

Select option (1-6): 
```

## First-Time User Flow

1. Start the application
2. Add your first task:
   - Select "1" (Add Task)
   - Enter title: "Buy groceries"
   - Enter description (optional): "Milk, eggs, bread"
3. View tasks:
   - Select "2" (View Tasks)
   - See your task listed as incomplete [ ]
4. Mark task complete:
   - Select "4" (Mark Complete)
   - Enter task ID: "1"
5. View tasks again:
   - Select "2" (View Tasks)
   - See task marked as complete [x]
6. Exit:
   - Select "6" (Exit)

## Common Commands

| Action | Command | Notes |
|--------|---------|-------|
| Add task | Select option 1 | Title required, description optional |
| View all | Select option 2 | Shows all tasks with status |
| Update task | Select option 3 | Task ID required, new title/desc optional |
| Complete toggle | Select option 4 | Task ID required, toggles status |
| Delete task | Select option 5 | Task ID required, permanent removal |
| Exit app | Select option 6 | Exits application (data not saved) |

## Troubleshooting

**Issue**: "Command not found: python"
**Solution**: Use `python3` or add Python to PATH

**Issue**: "No module named 'src'"
**Solution**: Run from repository root, add PYTHONPATH=.

**Issue**: "uv command not found"
**Solution**: Install uv via curl or pip: `pip install uv`

**Issue**: "Permission denied"
**Solution**: On Linux/Mac, run: `chmod +x src/main.py`
