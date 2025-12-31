# CLI Contracts: Phase I - In-Memory Python Console Todo App

**Feature**: 001-console-todo
**Date**: 2025-12-31

## Contract 1: Main Menu Display

**Description**: Shows all available actions to user

**Output Format**:
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

**Requirements**:
- Displays 6 options always
- Option numbers are 1-6
- Labels are user-friendly
- Prompt accepts input and waits

## Contract 2: Add Task Interaction

**Description**: Collects new task information from user

**Input Prompts**:
```
Enter task title: [cursor]
Enter task description (optional, press Enter to skip): [cursor]
```

**Validation**:
- Title cannot be empty after strip()
- Title cannot be whitespace-only
- Description is optional (empty string valid)

**Success Output**:
```
Task added successfully! Task ID: 1
```

**Error Output**:
```
Error: Title cannot be empty
```

## Contract 3: View Tasks Display

**Description**: Shows all tasks with their status

**Empty State Output**:
```
No tasks found. Add a task to get started!
```

**Populated State Output**:
```
=== Your Tasks ====

ID  Status  Title                Description
--  ------  ----                -----------
1   [ ]     Buy groceries        
2   [x]     Call mom             Remind about birthday
3   [ ]     Read documentation  
```

**Format Rules**:
- ID column width: 3 chars
- Status column width: 8 chars
- [ ] for incomplete, [x] for complete
- Description truncated to 20 chars if longer
- Trailing spaces in title for padding

## Contract 4: Update Task Interaction

**Description**: Modifies existing task title or description

**Input Prompts**:
```
Enter task ID to update: [cursor]
Enter new title (or press Enter to keep current): [cursor]
Enter new description (or press Enter to keep current): [cursor]
```

**Validation**:
- Task ID must exist in storage
- If title provided, cannot be empty/whitespace
- Empty input keeps current value

**Success Output**:
```
Task 1 updated successfully!
```

**Error Output**:
```
Error: Task ID not found
Error: Title cannot be empty
```

## Contract 5: Mark Complete Interaction

**Description**: Toggles task completion status

**Input Prompt**:
```
Enter task ID to toggle status: [cursor]
```

**Validation**:
- Task ID must exist in storage

**Success Output**:
```
Task 1 marked as complete!
or
Task 1 marked as incomplete!
```

**Error Output**:
```
Error: Task ID not found
```

## Contract 6: Delete Task Interaction

**Description**: Removes task from storage

**Input Prompt**:
```
Enter task ID to delete: [cursor]
```

**Validation**:
- Task ID must exist in storage

**Success Output**:
```
Task 1 deleted successfully!
```

**Error Output**:
```
Error: Task ID not found
```

**Confirmation Behavior**: No confirmation prompt (per Phase I simplicity)

## Contract 7: Exit Behavior

**Description**: Terminates application

**Output**:
```
Goodbye! Tasks will not be saved (in-memory only).
```

**Behavior**:
- Application terminates gracefully
- No data persistence (Phase I)
- No cleanup needed (in-memory storage)

## Contract 8: Invalid Input Handling

**Description**: User input doesn't match expected format

**Error Messages**:
```
Error: Invalid option. Please select 1-6.
Error: Invalid task ID. Please enter a number.
Error: Task ID not found.
```

**Recovery**: Returns to main menu after error message
