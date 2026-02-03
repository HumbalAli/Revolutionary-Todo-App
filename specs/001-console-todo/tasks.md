# Tasks: Phase I - In-Memory Python Console Todo App

**Input**: Design documents from `/specs/001-console-todo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below do NOT include test tasks. Tests are OPTIONAL - only include them if explicitly requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with uv venv
- [ ] T003 [P] Configure pyproject.toml for pytest
- [ ] T004 [P] Create requirements.txt with pytest

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Task dataclass in src/models/task.py with id, title, description, completed fields
- [ ] T006 Create storage module in src/services/storage.py with tasks list and tasks_by_id dict
- [ ] T007 Create next_id counter in storage module
- [ ] T008 Create add_task function in storage module
- [ ] T009 Create get_task function in storage module
- [ ] T010 Create get_all_tasks function in storage module
- [ ] T011 Create update_task function in storage module
- [ ] T012 Create delete_task function in storage module
- [ ] T013 Create toggle_complete function in storage module

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Task List (Priority: P1) MVP

**Goal**: Display all tasks with their completion status indicators

**Independent Test**: Can be fully tested by starting application and selecting View Tasks - displays task list interface with status indicators

### Implementation for User Story 1

- [ ] T014 [P] [US1] Create display_menu function in src/cli/menu.py
- [ ] T015 [P] [US1] Create format_task_table function in src/cli/display.py
- [ ] T016 [P] [US1] Create display_tasks function in src/cli/display.py
- [ ] T017 [P] [US1] Create display_empty_message function in src/cli/display.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testably independently

---

## Phase 4: User Story 2 - Add Task (Priority: P1) MVP

**Goal**: Create new tasks with title and optional description

**Independent Test**: Can be fully tested by selecting Add Task, entering title and description, confirming creation, and then viewing task list

### Implementation for User Story 2

- [ ] T018 [P] [US2] Create get_user_input function in src/cli/commands.py
- [ ] T019 [P] [US2] Create validate_title function in src/cli/commands.py
- [ ] T020 [US2] Create add_task_command function in src/cli/commands.py (depends on T019)
- [ ] T021 [P] [US2] Create display_success_message function in src/cli/display.py
- [ ] T022 [P] [US2] Create display_error_message function in src/cli/display.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark as Complete (Priority: P1) MVP

**Goal**: Toggle task completion status between complete and incomplete states

**Independent Test**: Can be fully tested by viewing tasks, selecting task ID to mark complete, viewing again to confirm status change

### Implementation for User Story 3

- [ ] T023 [US3] Create mark_complete_command function in src/cli/commands.py
- [ ] T024 [P] [US3] Create display_status_toggle function in src/cli/display.py

**Checkpoint**: All user stories P1 should now be independently functional

---

## Phase 6: User Story 4 - Update Task (Priority: P2)

**Goal**: Modify existing task title and description

**Independent Test**: Can be fully tested by adding a task, selecting Update Task, providing new title/description, and viewing task list

### Implementation for User Story 4

- [ ] T025 [US4] Create update_task_command function in src/cli/commands.py
- [ ] T026 [P] [US4] Update display functions to show update success in src/cli/display.py

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Delete Task (Priority: P2)

**Goal**: Permanently remove task from task list

**Independent Test**: Can be fully tested by adding a task, selecting Delete Task with task ID, and viewing task list

### Implementation for User Story 5

- [ ] T027 [US5] Create delete_task_command function in src/cli/commands.py
- [ ] T028 [P] [US5] Update display functions to show delete success in src/cli/display.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T029 [P] Create main menu router in src/cli/menu.py
- [ ] T030 Create exit command handler in src/cli/commands.py
- [ ] T031 Create invalid input error handler in src/cli/commands.py
- [ ] T032 Create main.py entry point in src/main.py
- [ ] T033 Add error handling for invalid task IDs in all commands
- [ ] T034 Code cleanup and refactoring
- [ ] T035 Performance optimization across all stories
- [ ] T036 Update README.md with usage examples
- [ ] T037 Validate all operations complete under 3 seconds performance goal

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 -> P2)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Models before services
- Services before commands
- Commands before display
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All display functions marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all display functions for User Story 1 together:
Task: "Create format_task_table function in src/cli/display.py"
Task: "Create display_tasks function in src/cli/display.py"
Task: "Create display_empty_message function in src/cli/display.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. Complete Phase 4: User Story 2
5. Complete Phase 5: User Story 3
6. **STOP AND VALIDATE**: Test User Stories 1-3 independently
7. Run application manually to verify MVP functionality

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test independently -> Demo (MVP read-only)
3. Add User Story 2 -> Test independently -> Demo
4. Add User Story 3 -> Test independently -> Demo
5. Add User Story 4 -> Test independently -> Demo
6. Add User Story 5 -> Test independently -> Demo
7. Complete Polish -> Full feature complete

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + 2
   - Developer B: User Story 3 + 4
   - Developer C: User Story 5 + Polish
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests were NOT explicitly requested in feature specification
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence