<!--
Sync Impact Report:
  Version change: none -> 1.0.0 (initial constitution)
  Modified principles: N/A (new constitution)
  Added sections: All sections
  Removed sections: N/A
  Templates requiring updates:
    - plan-template.md: Constitution Check section needs alignment with phase-based workflow
    - spec-template.md: Aligned with spec-driven development
    - tasks-template.md: Aligned with phase-based structure
    - phr-template.prompt.md: No changes needed
  Follow-up TODOs: None
-->

# Hackathon II - Todo App Evolution Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All code MUST be generated via Claude Code from specifications. Manual coding is prohibited. The development workflow strictly follows:

1. Feature specification created via `/sp.specify`
2. Implementation plan generated via `/sp.plan`
3. Actionable tasks derived via `/sp.tasks`
4. Code implemented via `/sp.implement`

Every code change MUST trace back to spec/plan/tasks. Direct coding without documentation is a violation of this principle.

**Rationale**: Ensures traceability, enables incremental delivery, prevents technical debt from unstructured changes, and supports the hackathon's requirement for demonstrable, documented progress.

### II. Phase-Based Evolution

The application evolves through five distinct phases, in strict sequential order:

1. **Phase I (Console)**: Python CLI with in-memory storage
2. **Phase II (Web)**: Next.js + FastAPI with Neon PostgreSQL
3. **Phase III (Chatbot)**: OpenAI ChatKit + Agents SDK with conversational interface
4. **Phase IV (Local K8s)**: Docker + Minikube with Helm charts
5. **Phase V (Cloud)**: Kafka + Dapr on cloud Kubernetes with event-driven architecture

Phases MUST NOT be skipped. Each phase must be completed with a working application and demo video before proceeding to the next.

**Rationale**: Incremental complexity management, validation at each stage, ensures functional foundation before architectural evolution, aligns with hackathon submission requirements.

### III. Monorepo Organization

Single repository structure with clear frontend/backend separation:

```
todo-app/
├── backend/          # API and business logic (FastAPI)
├── frontend/         # UI and client-side (Next.js)
├── infra/            # Docker, Kubernetes, Helm charts
└── specs/            # Feature specifications
```

All phases use the same monorepo. New project structures must be justified via ADR.

**Rationale**: Simplifies dependency management, enables code sharing between phases, provides single source of truth for CI/CD, supports incremental addition of complexity.

### IV. Clean Code Standards

All code MUST adhere to:

- Descriptive names: Variables, functions, and classes use self-documenting names
- Docstrings: Every public function/class has docstring with purpose, parameters, and returns
- Proper structure: Modules organized by responsibility, clear separation of concerns
- Type hints: Required for Python (type annotations), TypeScript strict mode for frontend

Code review MUST reject violations. Linting and formatting tools are required.

**Rationale**: Maintainability, readability, reduced onboarding time, enables AI agents to understand and modify code effectively.

### V. WSL 2 for Windows

All development commands MUST execute within WSL 2 (Windows Subsystem for Linux) on Windows platforms. Native Windows commands are prohibited for build, test, and deployment operations.

**Rationale**: Consistent Linux environment, avoids platform-specific issues, enables proper toolchain support for Python, Docker, and Kubernetes tools.

### VI. Security & Secrets

All sensitive data MUST be externalized:

- Environment variables via `.env` files (never committed)
- No hardcoded credentials in code
- Secrets managed via secure mechanisms (Kubernetes secrets, Dapr secret stores)
- JWT tokens for authentication between frontend and backend

**Rationale**: Prevents credential leakage, enables different configurations per environment, aligns with cloud-native security best practices.

### VII. AI-First Development

The application prioritizes AI integration:

- OpenAI Agents SDK for agent logic
- Model Context Protocol (MCP) tools for conversational interfaces
- Stateless chat endpoints for scalability
- AI agents used as subagents for reusable intelligence

All AI interactions are traceable via Prompt History Records (PHRs).

**Rationale**: Future-proof architecture, leverages AI capabilities for competitive advantage, maintains auditability of AI-generated decisions.

### VIII. Cloud-Native Architecture

The application follows cloud-native patterns:

- Containerization: Docker for all services
- Orchestration: Kubernetes (Minikube for local, cloud K8s for production)
- Event-driven: Kafka (Redpanda/Strimzi) for async communication
- Sidecar pattern: Dapr for distributed primitives
- Infrastructure as Code: Helm charts for deployment

**Rationale**: Scalability, portability, resilience, alignment with modern cloud practices, enables horizontal scaling.

## Technology Stack

### Phase I: Console Application
- Language: Python 3.13+
- Package manager: uv
- Storage: In-memory (Python data structures)
- CLI framework: argparse or Typer
- Testing: pytest

### Phase II: Web Application
- Frontend: Next.js 16+ (App Router)
- Backend: FastAPI with async support
- Database: Neon PostgreSQL
- ORM: SQLModel
- Authentication: Better Auth with JWT
- Testing: pytest (backend), Playwright (frontend)

### Phase III: Chatbot Interface
- Chat UI: OpenAI ChatKit
- Agent framework: OpenAI Agents SDK
- MCP: Official MCP SDK for tool integration
- API endpoint: Stateless chat (session state in Redis or database)

### Phase IV: Local Kubernetes
- Containerization: Docker
- Orchestration: Minikube
- Package management: Helm charts
- AI assistance: kubectl-ai, Kagent, Gordon (Docker AI)

### Phase V: Cloud Native
- Event streaming: Kafka (Redpanda or Strimzi)
- Distributed runtime: Dapr
- Kubernetes providers: DigitalOcean DOKS, Azure AKS, or Google GKE
- Architecture: Event-driven with pub/sub patterns

## Key Standards

### Code Traceability
- All code changes map back to spec/plan/tasks
- Use Claude Code Subagents for reusable intelligence
- PHRs created for every significant AI interaction

### Development Workflow
1. Clarify requirements via `/sp.clarify`
2. Create spec via `/sp.specify`
3. Plan architecture via `/sp.plan`
4. Generate tasks via `/sp.tasks`
5. Implement via `/sp.implement`
6. Review and adjust via ADRs

### Authentication
- Better Auth with JWT for frontend/backend communication
- JWT tokens stored securely (httpOnly cookies or secure storage)
- Token refresh mechanism implemented

### Database
- Neon PostgreSQL for Phase II+
- SQLModel for ORM (provides Pydantic models + SQLAlchemy)
- Migration strategy: Alembic for schema evolution

## Constraints

### Non-Negotiable Constraints
- No manual coding allowed - MUST use spec-driven workflow
- All phases MUST be completed in order
- WSL 2 required for Windows users
- Demo video under 90 seconds for each phase submission

### Development Constraints
- All code generated by Claude Code from specs
- No direct git commits without spec traceability
- Feature flags used for gradual rollout
- Zero-downtime deployments in Phase V

### Technology Constraints
- Technology stack is fixed per phase - substitutions require ADR
- Version specifications are minimum requirements
- Compatibility layers only justified via ADR

## Governance

### Amendment Procedure
- Proposals MUST document the change, rationale, and impact on existing work
- Amendments require consensus approval
- Version MUST be updated per semantic versioning:
  - MAJOR: Backward incompatible principle removal or redefinition
  - MINOR: New principle or section added
  - PATCH: Clarifications, wording, typo fixes
- Migration plan MUST be included for breaking changes

### Compliance Review
- All PRs MUST verify compliance with this constitution
- Constitution Check gates MUST pass before implementation
- Complexities MUST be justified in plan.md
- Violations MUST be documented with ADR explaining necessity

### Versioning Policy
- Increment version based on semantic versioning rules
- Document version change in Sync Impact Report
- Update dependent templates to reflect principle changes
- Maintain version history for traceability

**Version**: 1.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2025-12-31
