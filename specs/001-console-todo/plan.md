# Implementation Plan: Phase I - In-Memory Python Console Todo App

**Branch**: `001-console-todo` | **Date**: 2025-12-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-console-todo/spec.md`

## Summary

Python command-line todo application with in-memory storage supporting 5 core CRUD operations: Add Task, View Tasks, Update Task, Mark Complete, Delete Task. Users interact via text-based menu. Tasks are stored in memory only (lost on exit). This is Phase I of the 5-phase evolution path toward cloud-native architecture.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: argparse (built-in), pytest (testing)
**Storage**: In-memory (Python List[Task] + Dict[int, Task])
**Testing**: pytest
**Target Platform**: Linux/WSL 2 (per constitution)
**Project Type**: single (CLI application)
**Performance Goals**: All operations complete under 3 seconds for under 1000 tasks
**Constraints**: In-memory only (no persistence), single-user (no concurrency)
**Scale/Scope**: 1 user, under 1000 tasks in memory

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | Code will be generated from spec/plan/tasks via `/sp.implement` |
| II. Phase-Based Evolution | PASS | Phase I scope only (console, in-memory, no persistence) |
| III. Monorepo Organization | PASS | Single project structure (src/, tests/) |
| IV. Clean Code Standards | PASS | PEP 8, docstrings, type hints planned |
| V. WSL 2 for Windows | PASS | All commands execute in WSL 2 environment |
| VI. Security & Secrets | PASS | No credentials needed for in-memory CLI |
| VII. AI-First Development | N/A | Phase III+ (not applicable to Phase I) |
| VIII. Cloud-Native Architecture | N/A | Phase IV+ (not applicable to Phase I) |

**Result**: All gates PASS. No constitution violations. Ready to proceed.

## Project Structure

### Documentation (this feature)

```
specs/001-console-todo/
|   plan.md              # This file (/sp.plan command output)
|   research.md          # Phase 0 output (/sp.plan command)
|   data-model.md        # Phase 1 output (/sp.plan command)
|   quickstart.md        # Phase 1 output (/sp.plan command)
|   contracts/           # Phase 1 output (/sp.plan command)
|   |   |   -- cli-contracts.md
|   tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```
src/
|   models/
|   |   |   -- task.py            # Task dataclass with id, title, description, completed
|   services/
|   |   |   -- storage.py          # In-memory task storage (list + dict)
|   |   |   -- todo_service.py    # Business logic for CRUD operations
|   cli/
|   |   -- menu.py             # Main menu display and routing
|   |   -- commands.py          # CLI input handling and validation
|   |   -- display.py          # Output formatting (tables, messages)
|   -- main.py              # Application entry point

tests/
|   unit/
|   |   -- test_task.py         # Task dataclass tests
|   |   -- test_storage.py      # Storage service tests
|   |   -- test_todo_service.py # Business logic tests
|   -- integration/
|   |   |   -- test_cli_flow.py    # End-to-end CLI workflow tests
```

**Structure Decision**: Single project structure with clear separation: models (data), services (logic), cli (interface). This aligns with Phase I scope and enables clean evolution to Phase II (backend separation).

## Complexity Tracking

> No constitution violations. This section intentionally left blank.

## Phase 0: Research Summary

See [research.md](research.md) for complete research findings.

**Key Decisions**:
- CLI Framework: argparse (built-in, no external dependency)
- Storage: In-memory using List[Task] + Dict[int, Task] for iteration and lookup
- Task IDs: Sequential integers starting at 1, never re-used
- Validation: String strip() for empty/whitespace detection
- Error Handling: try/except blocks with specific exception types
- Output: Simple text-based tables with padding

## Phase 1: Design Summary

### Data Model

See [data-model.md](data-model.md) for complete data model specification.

**Key Entity**: Task (dataclass with id: int, title: str, description: str, completed: bool)

**Storage Structures**:
```python
tasks: List[Task] = []              # For iteration/display
tasks_by_id: Dict[int, Task] = {}    # For O(1) lookup by ID
next_id: int = 1                    # Auto-increment counter
```

### Contracts

See [contracts/cli-contracts.md](contracts/cli-contracts.md) for complete CLI contract specifications.

**Contract Coverage**:
1. Main Menu Display - 6 options with numbered prompts
2. Add Task - Title required, description optional
3. View Tasks - Table format with ID, status, title, description
4. Update Task - Modify title/description by ID
5. Mark Complete - Toggle completion status by ID
6. Delete Task - Remove task by ID
7. Exit Behavior - Graceful termination
8. Invalid Input Handling - Clear error messages

### Quickstart

See [quickstart.md](quickstart.md) for installation and usage instructions.

**Prerequisites**:
- Python 3.13+
- uv package manager
- Terminal/CLI access

**Installation**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
uv pip install pytest
```

**Running**:
```bash
python src/main.py
```