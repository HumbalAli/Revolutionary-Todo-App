# Tasks: Advanced Cloud Deployment with Kafka, Dapr, and Event-Driven Architecture

**Input**: Design documents from `/specs/005-kafka-dapr-architecture/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested - test tasks omitted (add via TDD if needed)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`, `infra/`
- Structure based on plan.md monorepo layout

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, Kafka/Dapr infrastructure setup

- [X] T001 Create database migration for AdvancedTask extended columns in backend/src/models/migrations/
- [X] T002 Create Dapr components directory structure in infra/dapr/components/
- [X] T003 [P] Create Strimzi Kafka cluster configuration in infra/kafka/strimzi/kafka-cluster.yaml
- [X] T004 [P] Create Redpanda configuration in infra/kafka/redpanda/redpanda-config.yaml
- [X] T005 [P] Install python-dateutil for RRule parsing in backend/requirements.txt
- [X] T006 [P] Install dapr Python SDK in backend/requirements.txt
- [X] T007 Update Helm chart values.yaml with Kafka and Dapr configuration in infra/helm/todo-chatbot/values.yaml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create Dapr pub/sub component configuration for Kafka in infra/dapr/components/pubsub.yaml
- [X] T009 Create Dapr state store component configuration for PostgreSQL in infra/dapr/components/statestore.yaml
- [X] T010 Create Dapr secrets component configuration for Kubernetes in infra/dapr/components/secrets.yaml
- [X] T011 Create Dapr cron binding component configuration in infra/dapr/components/bindings.yaml
- [X] T012 [P] Create TaskEvent model in backend/src/models/event_models.py
- [X] T013 [P] Create Reminder model in backend/src/models/event_models.py
- [X] T014 [P] Create UserProfile model in backend/src/models/event_models.py
- [X] T015 [P] Create RecurringRule model in backend/src/models/event_models.py
- [X] T016 Create Kafka service base class with producer/consumer in backend/src/services/kafka_service.py
- [X] T017 Create Dapr pub/sub handler base in backend/src/api/dapr/pubsub.py
- [X] T018 Create Dapr state management service in backend/src/api/dapr/state.py
- [X] T019 Create Dapr bindings handler in backend/src/api/dapr/bindings.py
- [X] T020 Create Kafka topics definition for Helm in infra/helm/todo-chatbot/templates/kafka-topics.yaml
- [X] T021 Update backend Dockerfile with Dapr sidecar support in infra/docker/backend/Dockerfile
- [X] T022 Add Dapr annotations to backend deployment in infra/helm/todo-chatbot/templates/backend-deployment.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create and Manage Advanced Task Properties (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with due dates, priorities, tags, and recurrence patterns

**Independent Test**: Create a task with all advanced properties via API, verify persistence and retrieval

### Implementation for User Story 1

- [X] T023 [P] [US1] Extend Task model with due_date, priority, tags fields in backend/src/models/todo_models.py
- [X] T024 [P] [US1] Add recurrence_rule, recurrence_parent_id, is_recurring fields to Task model in backend/src/models/todo_models.py
- [X] T025 [P] [US1] Add reminder_offset_minutes, recurrence_count fields to Task model in backend/src/models/todo_models.py
- [X] T026 [P] [US1] Add search_vector tsvector column for full-text search in backend/src/models/todo_models.py
- [ ] T027 [US1] Create database migration for new Task columns in backend/src/models/migrations/add_advanced_task_fields.py
- [X] T028 [US1] Create recurring task service with RRule parsing in backend/src/services/recurring_service.py
- [X] T029 [US1] Implement generate_next_occurrence method in recurring_service.py
- [ ] T030 [US1] Extend TaskCreate schema with advanced properties in backend/src/api/routes/tasks.py
- [ ] T031 [US1] Extend TaskUpdate schema with advanced properties in backend/src/api/routes/tasks.py
- [ ] T032 [US1] Update POST /tasks endpoint to handle advanced properties in backend/src/api/routes/tasks.py
- [ ] T033 [US1] Update PUT /tasks/{id} endpoint to handle advanced properties in backend/src/api/routes/tasks.py
- [ ] T034 [US1] Implement POST /tasks/{id}/complete endpoint with recurring task generation in backend/src/api/routes/tasks.py
- [ ] T035 [US1] Publish task.created event to Kafka on task creation in backend/src/services/kafka_service.py
- [ ] T036 [US1] Publish task.completed event to Kafka on task completion in backend/src/services/kafka_service.py
- [ ] T037 [P] [US1] Create TaskForm component with due date picker in frontend/src/components/TaskForm.tsx
- [ ] T038 [P] [US1] Create PrioritySelector component in frontend/src/components/PriorityTags.tsx
- [ ] T039 [P] [US1] Create TagInput component in frontend/src/components/PriorityTags.tsx
- [ ] T040 [P] [US1] Create RecurringConfig component with RRule presets in frontend/src/components/RecurringConfig.tsx
- [ ] T041 [US1] Extend frontend API service with advanced task properties in frontend/src/services/api.ts
- [ ] T042 [US1] Update task type definitions with advanced properties in frontend/src/types/task.ts
- [ ] T043 [US1] Integrate advanced property components into TaskForm in frontend/src/components/TaskForm.tsx

**Checkpoint**: User Story 1 complete - users can create tasks with advanced properties

---

## Phase 4: User Story 2 - Receive Timely Reminders and Notifications (Priority: P1)

**Goal**: Users receive reminder notifications when task due dates approach

**Independent Test**: Create a task with due date, verify reminder event is published and processed

### Implementation for User Story 2

- [ ] T044 [P] [US2] Create reminder service with due date checking in backend/src/services/reminder_service.py
- [ ] T045 [P] [US2] Implement check_due_reminders method that queries tasks approaching due date in backend/src/services/reminder_service.py
- [ ] T046 [P] [US2] Implement create_reminder method for new tasks with due dates in backend/src/services/reminder_service.py
- [ ] T047 [US2] Create Dapr cron binding handler for reminder checks in backend/src/api/dapr/bindings.py
- [ ] T048 [US2] Implement reminder.due event publisher in backend/src/services/kafka_service.py
- [ ] T049 [US2] Create reminder consumer service in backend/src/services/reminder_consumer.py
- [ ] T050 [US2] Implement reminder.sent event publisher after delivery in backend/src/services/reminder_consumer.py
- [ ] T051 [US2] Create reminder status update endpoint GET /tasks/{id}/reminders in backend/src/api/routes/tasks.py
- [ ] T052 [US2] Implement idempotent reminder delivery (track sent reminders) in backend/src/services/reminder_service.py
- [ ] T053 [US2] Update Reminder model with retry_count and error handling in backend/src/models/event_models.py
- [ ] T054 [P] [US2] Create NotificationBanner component for frontend alerts in frontend/src/components/NotificationBanner.tsx
- [ ] T055 [US2] Add WebSocket subscription for real-time reminder notifications in frontend/src/services/api.ts

**Checkpoint**: User Story 2 complete - users receive timely reminders for due tasks

---

## Phase 5: User Story 3 - Search and Filter Tasks Efficiently (Priority: P2)

**Goal**: Users can search, filter, and sort tasks by various criteria

**Independent Test**: Create multiple tasks with different properties, verify search/filter/sort returns correct results

### Implementation for User Story 3

- [ ] T056 [P] [US3] Create database indexes for search optimization in backend/src/models/migrations/add_search_indexes.py
- [ ] T057 [P] [US3] Add GIN index on search_vector for full-text search in migration
- [ ] T058 [P] [US3] Add GIN index on tags array column in migration
- [ ] T059 [P] [US3] Add B-tree indexes on priority, due_date, status in migration
- [ ] T060 [US3] Implement full-text search query builder in backend/src/services/task_service.py
- [ ] T061 [US3] Implement filter builder for priority, status, tags in backend/src/services/task_service.py
- [ ] T062 [US3] Implement sort builder for due_date, priority, title, created_at in backend/src/services/task_service.py
- [ ] T063 [US3] Update GET /tasks endpoint with search, filter, sort query params in backend/src/api/routes/tasks.py
- [ ] T064 [US3] Add pagination support with limit/offset to GET /tasks in backend/src/api/routes/tasks.py
- [ ] T065 [US3] Implement search_vector trigger/update on task save in backend/src/models/todo_models.py
- [ ] T066 [P] [US3] Create TaskFilters component with search input in frontend/src/components/TaskFilters.tsx
- [ ] T067 [P] [US3] Add priority filter dropdown to TaskFilters in frontend/src/components/TaskFilters.tsx
- [ ] T068 [P] [US3] Add status filter checkbox group to TaskFilters in frontend/src/components/TaskFilters.tsx
- [ ] T069 [P] [US3] Add tag filter with autocomplete to TaskFilters in frontend/src/components/TaskFilters.tsx
- [ ] T070 [P] [US3] Add date range filter to TaskFilters in frontend/src/components/TaskFilters.tsx
- [ ] T071 [P] [US3] Create SortSelector component in frontend/src/components/TaskFilters.tsx
- [ ] T072 [US3] Update task list API call to include filter/sort params in frontend/src/services/api.ts
- [ ] T073 [US3] Integrate TaskFilters into main page in frontend/src/pages/index.tsx
- [ ] T074 [US3] Add URL query params for filter persistence in frontend/src/pages/index.tsx

**Checkpoint**: User Story 3 complete - users can efficiently search/filter/sort tasks

---

## Phase 6: User Story 4 - Seamless Cloud Deployment (Priority: P3)

**Goal**: Application deployed to cloud Kubernetes with event-driven architecture

**Independent Test**: Deploy to cloud cluster, verify all services running and events flowing through Kafka

### Implementation for User Story 4

- [ ] T075 [P] [US4] Create DigitalOcean DOKS deployment guide in specs/005-kafka-dapr-architecture/deployment/doks-guide.md
- [ ] T076 [P] [US4] Create Azure AKS deployment guide in specs/005-kafka-dapr-architecture/deployment/aks-guide.md
- [ ] T077 [P] [US4] Create Google GKE deployment guide in specs/005-kafka-dapr-architecture/deployment/gke-guide.md
- [ ] T078 [US4] Create GitHub Actions workflow for CI in .github/workflows/ci.yaml
- [ ] T079 [US4] Add Docker build and push step to CI workflow in .github/workflows/ci.yaml
- [ ] T080 [US4] Add Helm deployment step to CI workflow in .github/workflows/ci.yaml
- [ ] T081 [US4] Create Kubernetes secrets manifest template in infra/helm/todo-chatbot/templates/secrets.yaml
- [ ] T082 [US4] Add Dapr component manifests to Helm chart in infra/helm/todo-chatbot/templates/dapr-components/
- [ ] T083 [US4] Create PodDisruptionBudget for zero-downtime updates in infra/helm/todo-chatbot/templates/pdb.yaml
- [ ] T084 [US4] Update readiness probes to check Kafka and Dapr health in infra/helm/todo-chatbot/templates/backend-deployment.yaml
- [ ] T085 [US4] Create database migration Job for Helm in infra/helm/todo-chatbot/templates/migration-job.yaml
- [ ] T086 [US4] Update Chart.yaml version for Phase V release in infra/helm/todo-chatbot/Chart.yaml
- [ ] T087 [US4] Create cloud-specific values files (values-doks.yaml, values-aks.yaml, values-gke.yaml) in infra/helm/todo-chatbot/

**Checkpoint**: User Story 4 complete - application deployed to cloud with full event-driven architecture

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T088 [P] Update README.md with Phase V features and deployment instructions
- [ ] T089 [P] Create audit log consumer for task-events topic in backend/src/services/audit_consumer.py
- [ ] T090 [P] Implement real-time sync consumer for task-updates topic in backend/src/services/sync_consumer.py
- [ ] T091 Create user profile endpoint GET /profile in backend/src/api/routes/profile.py
- [ ] T092 Create user profile endpoint PUT /profile in backend/src/api/routes/profile.py
- [ ] T093 Add error handling for Kafka connection failures in backend/src/services/kafka_service.py
- [ ] T094 Add Dapr health check endpoint integration in backend/src/main.py
- [ ] T095 Add event schema validation in Kafka producers in backend/src/services/kafka_service.py
- [ ] T096 Update TaskItemEnhanced component with all advanced features in frontend/src/components/TaskItemEnhanced.tsx
- [ ] T097 Run quickstart.md validation - verify local Minikube deployment
- [ ] T098 Run quickstart.md validation - verify cloud deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US2 can proceed in parallel after Foundational
  - US3 depends on T023-T026 (extended Task model from US1)
  - US4 can proceed independently after Foundational
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Foundation for other stories
- **User Story 2 (P1)**: Can start after Foundational - Uses Reminder model from Phase 2
- **User Story 3 (P2)**: Depends on Task model extensions from US1 (T023-T026)
- **User Story 4 (P3)**: Can start after Foundational - Infrastructure focused

### Within Each User Story

- Models before services
- Services before endpoints
- Backend before frontend
- Core implementation before integration

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004 in parallel (Kafka configs)
- T005, T006 in parallel (Python dependencies)

**Phase 2 (Foundational)**:
- T008-T011 in parallel (Dapr components)
- T012-T015 in parallel (Event models)

**Phase 3 (US1)**:
- T023-T026 in parallel (Task model extensions)
- T037-T040 in parallel (Frontend components)

**Phase 4 (US2)**:
- T044-T046 in parallel (Reminder service methods)

**Phase 5 (US3)**:
- T056-T059 in parallel (Database indexes)
- T066-T071 in parallel (Frontend filter components)

**Phase 6 (US4)**:
- T075-T077 in parallel (Deployment guides)

---

## Parallel Example: User Story 1

```bash
# Launch all Task model extensions together:
Task: "Extend Task model with due_date, priority, tags fields in backend/src/models/todo_models.py"
Task: "Add recurrence_rule, recurrence_parent_id, is_recurring fields to Task model"
Task: "Add reminder_offset_minutes, recurrence_count fields to Task model"
Task: "Add search_vector tsvector column for full-text search"

# Launch all frontend components together:
Task: "Create TaskForm component with due date picker in frontend/src/components/TaskForm.tsx"
Task: "Create PrioritySelector component in frontend/src/components/PriorityTags.tsx"
Task: "Create TagInput component in frontend/src/components/PriorityTags.tsx"
Task: "Create RecurringConfig component with RRule presets in frontend/src/components/RecurringConfig.tsx"
```

---

## Parallel Example: User Story 3

```bash
# Launch all database index migrations together:
Task: "Add GIN index on search_vector for full-text search in migration"
Task: "Add GIN index on tags array column in migration"
Task: "Add B-tree indexes on priority, due_date, status in migration"

# Launch all frontend filter components together:
Task: "Create TaskFilters component with search input"
Task: "Add priority filter dropdown to TaskFilters"
Task: "Add status filter checkbox group to TaskFilters"
Task: "Add tag filter with autocomplete to TaskFilters"
Task: "Add date range filter to TaskFilters"
Task: "Create SortSelector component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Advanced Task Properties)
4. **STOP and VALIDATE**: Test creating/managing tasks with advanced properties
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test reminders → Deploy/Demo
4. Add User Story 3 → Test search/filter → Deploy/Demo
5. Add User Story 4 → Test cloud deployment → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Backend) + User Story 3 (depends on US1 models)
   - Developer B: User Story 2 (Reminder system)
   - Developer C: User Story 4 (Infrastructure/Deployment)
   - Developer D: User Story 1 (Frontend) + User Story 3 (Frontend)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- US1 is MVP - delivers core advanced task functionality
- US2 adds real-time value with reminders
- US3 improves UX with search/filter
- US4 enables production deployment
