# Research: Phase I - In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Date**: 2025-12-31
**Purpose**: Technical decisions for Python console todo application

## CLI Framework Decision

**Decision**: argparse (standard library)

**Rationale**: 
- No external dependency required
- Built into Python 3.13+ (no uv dependency)
- Sufficient for simple menu-driven interface
- Aligns with Phase I constraint of minimal dependencies

**Alternatives considered**:
- Typer: More features but external dependency
- Click: Popular but external dependency
- Custom input parsing: More code, less tested

## Storage Strategy

**Decision**: In-memory Python list/dict structure

**Rationale**:
- Phase I explicitly requires in-memory (no database)
- Simpler than file-based for initial learning
- Data lost on exit is acceptable (Phase I scope)
- Aligns with spec requirements

**Structure**:
```python
tasks: List[Task]  # List for iteration
task_dict: Dict[int, Task]  # Dict for O(1) lookup by ID
next_id: int  # Counter for unique ID assignment
```

## Task ID Strategy

**Decision**: Sequential integers starting at 1, never re-used

**Rationale**:
- Simple and predictable for users
- No re-use prevents confusion after deletions
- Aligns with spec FR-002 and assumption

## Input Validation Approach

**Decision**: Simple string validation with strip() for whitespace

**Rationale**:
- Handles empty string and whitespace-only cases
- Simple to implement without external validators
- Sufficient for Phase I scope

**Pattern**:
```python
title = input("Title: ").strip()
if not title:
    print("Error: Title cannot be empty")
    # handle error
```

## Description Handling

**Decision**: Accept multi-line and special characters as-is

**Rationale**:
- Aligns with spec FR-014
- No sanitization needed for in-memory storage
- Display back as input (preserves formatting)

## Error Handling Pattern

**Decision**: try/except blocks with specific exception types

**Rationale**:
- Prevents crashes on invalid input
- Provides clear error messages (spec FR-011)
- Standard Python practice

## Output Formatting

**Decision**: Simple text-based table layout

**Rationale**:
- No external table libraries needed
- Console-friendly
- Clear separation of columns with padding

**Pattern**:
```
ID  Status  Title                Description
--  ------  ----                -----------
1   [ ]     Buy groceries        
2   [x]     Call mom             Remind about birthday
```

## Exit Strategy

**Decision**: Simple break from main loop on "Exit" or "q" input

**Rationale**:
- Graceful termination (spec FR-013)
- No cleanup needed for in-memory data
- Standard CLI pattern
