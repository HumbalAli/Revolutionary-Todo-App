# Implementation Plan: Advanced Cloud Deployment with Kafka, Dapr, and Event-Driven Architecture

**Branch**: `005-kafka-dapr-architecture` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-kafka-dapr-architecture/spec.md`

## Summary

This phase (Phase V) implements advanced task management features with an event-driven microservices architecture using Kafka and Dapr. The system will support recurring tasks, due date reminders, priorities, tags, search/filter/sort capabilities, and deploy to cloud Kubernetes infrastructure. The architecture leverages Kafka for event streaming and Dapr for distributed application runtime capabilities including pub/sub, state management, service invocation, cron bindings, and secrets management.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**: FastAPI 0.104+, Next.js 16+, Dapr SDK, Kafka client libraries, OpenAI Agents SDK, MCP SDK
**Storage**: Neon PostgreSQL (existing), Dapr state store (Redis or PostgreSQL), Kafka topics for events
**Testing**: pytest (backend), Playwright (frontend), integration tests for Kafka/Dapr
**Target Platform**: Cloud Kubernetes (Azure AKS, Google GKE, or DigitalOcean DOKS), Minikube (local)
**Project Type**: Web application with event-driven backend
**Performance Goals**: <2s search/filter response for 10K tasks, <5min reminder delivery, <1min recurring task generation
**Constraints**: 99.5% uptime, 99.9% Kafka delivery, zero-downtime deployment, backward compatible with Phase II-IV
**Scale/Scope**: Support 1000+ tasks per user, 10K concurrent users, event-driven architecture with 3 Kafka topics

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Status

✅ **Spec-Driven Development**: This plan generated from specification via `/sp.plan` command
✅ **Phase-Based Evolution**: This is Phase V, following completed Phases I-IV
✅ **Monorepo Organization**: Maintains existing monorepo structure with backend/frontend/infra
✅ **Clean Code Standards**: Will enforce type hints, docstrings, descriptive names
✅ **WSL 2 for Windows**: All commands executable in WSL 2 environment
✅ **Security & Secrets**: Dapr secrets management, no hardcoded credentials
✅ **AI-First Development**: Maintains OpenAI Agents SDK, MCP tools, stateless chat
✅ **Cloud-Native Architecture**: Adds Kafka (event-driven) and Dapr (sidecar pattern) to existing Docker/K8s setup

### Gates Passed

- **Technology Stack Alignment**: Uses prescribed Phase V technologies (Kafka, Dapr, Cloud K8s)
- **Backward Compatibility**: Extends Phase II-IV without breaking existing functionality
- **No New Projects**: Extends existing backend/frontend within monorepo
- **Traceability**: All changes map to spec requirements FR-001 through FR-011

### Post-Design Re-check

✅ **All gates remain passing after Phase 1 design**

**Verified**:
- Data model extends existing schema without breaking changes
- API contracts maintain backward compatibility (v2.0 alongside existing API)
- Kafka event schemas are versioned for evolution
- Dapr components use standard configuration patterns
- No new architectural complexity beyond Phase V requirements
- All design decisions documented in research.md
- Deployment strategy maintains zero-downtime updates

## Project Structure

### Documentation (this feature)

```text
specs/005-kafka-dapr-architecture/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── task-api-extended.yaml    # Extended task API with new properties
│   ├── kafka-events.yaml          # Kafka event schemas
│   └── dapr-components.yaml       # Dapr component configurations
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── todo_models.py          # Extended with AdvancedTask, RecurringRule
│   │   └── event_models.py         # NEW: TaskEvent, Reminder models
│   ├── services/
│   │   ├── task_service.py         # Extended with search/filter/sort
│   │   ├── recurring_service.py    # NEW: Handles recurring task logic
│   │   ├── reminder_service.py     # NEW: Reminder scheduling
│   │   └── kafka_service.py        # NEW: Kafka producer/consumer
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tasks.py            # Extended with new endpoints
│   │   │   └── events.py           # NEW: Event subscription endpoints
│   │   └── dapr/
│   │       ├── pubsub.py           # NEW: Dapr pub/sub handlers
│   │       ├── state.py            # NEW: Dapr state management
│   │       └── bindings.py         # NEW: Dapr cron bindings
│   └── agents/
│       └── task_agent.py           # Extended with new capabilities
└── tests/
    ├── unit/
    ├── integration/
    │   ├── test_kafka.py           # NEW: Kafka integration tests
    │   └── test_dapr.py            # NEW: Dapr integration tests
    └── e2e/

frontend/
├── src/
│   ├── components/
│   │   ├── TaskForm.tsx            # Extended with new fields
│   │   ├── TaskFilters.tsx         # NEW: Search/filter UI
│   │   ├── RecurringConfig.tsx     # NEW: Recurrence configuration
│   │   └── PriorityTags.tsx        # NEW: Priority and tag UI
│   ├── pages/
│   │   └── index.tsx               # Extended with filter/search
│   └── services/
│       └── api.ts                  # Extended with new endpoints
└── tests/

infra/
├── docker/
│   ├── backend/Dockerfile          # Updated with Dapr sidecar
│   └── frontend/Dockerfile         # No changes
├── helm/
│   └── todo-chatbot/
│       ├── values.yaml             # Extended with Kafka/Dapr config
│       ├── templates/
│       │   ├── kafka-topics.yaml   # NEW: Kafka topic definitions
│       │   ├── dapr-components/    # NEW: Dapr component specs
│       │   │   ├── pubsub.yaml
│       │   │   ├── statestore.yaml
│       │   │   ├── bindings.yaml
│       │   │   └── secrets.yaml
│       │   └── backend-deployment.yaml  # Updated with Dapr annotations
│       └── Chart.yaml              # Version bump
└── kafka/
    ├── strimzi/                    # NEW: Strimzi operator configs (self-hosted)
    └── redpanda/                   # NEW: Redpanda configs (alternative)
```

**Structure Decision**: Extends existing monorepo structure (Option 2: Web application) with new modules for event-driven capabilities. Adds infra/kafka for Kafka deployment options. Backend services layer extended with recurring_service, reminder_service, and kafka_service. Frontend components extended with filtering and recurring task UI. Maintains backward compatibility with existing Phase II-IV structure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All additions align with Phase V requirements in constitution and extend existing structure without introducing architectural complexity beyond what is prescribed.