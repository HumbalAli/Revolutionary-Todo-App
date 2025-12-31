---
id: 0001
title: Initial Constitution Creation
stage: constitution
date: 2025-12-31
surface: agent
model: claude-opus-4.5-20251101
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution","project-setup","hackathon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None
---

## Prompt

Project: Hackathon II - Todo App Evolution

Core principles:
- Spec-Driven Development (NON-NEGOTIABLE) - All code must be generated via Claude Code from specs, no manual coding
- Phase-Based Evolution - 5 phases in order: Console -> Web -> Chatbot -> Local K8s -> Cloud
- Monorepo Organization - Single repository with frontend/backend separation
- Clean Code Standards - Descriptive names, docstrings, proper structure
- WSL 2 for Windows - Use WSL 2 for all development commands
- Security & Secrets - Environment variables, no hardcoded credentials
- AI-First Development - OpenAI Agents SDK, MCP tools for conversational interface
- Cloud-Native Architecture - Docker, Kubernetes, event-driven with Kafka and Dapr

Key standards:
- All code changes must map back to spec/plan/tasks
- Use Claude Code Subagents for reusable intelligence
- Technology stack fixed per phase
- Better Auth with JWT for frontend/backend communication
- Neon PostgreSQL for database (Phase II+)
- OpenAI ChatKit for chatbot UI (Phase III+)

Technology Stack by Phase:
Phase I: Python 3.13+, uv, Claude Code, Spec-Kit Plus, in-memory storage
Phase II: Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth with JWT
Phase III: OpenAI ChatKit, OpenAI Agents SDK, Official MCP SDK, stateless chat endpoint
Phase IV: Docker, Minikube, Helm charts, kubectl-ai, Kagent, Gordon (Docker AI)
Phase V: Kafka (Redpanda/Strimzi), Dapr, DigitalOcean DOKS/Azure AKS/Google GKE, event-driven architecture

Constraints:
- No manual coding allowed - must use spec-driven workflow
- All phases must be completed in order
- WSL 2 required for Windows users
- Demo video under 90 seconds for each phase submission

Success criteria:
- All phases completed with working applications
- Specs/plan/tasks traceable for every feature
- Deployed applications at each phase
- Demo videos demonstrating features

## Response snapshot

Created initial project constitution v1.0.0 for Hackathon II - Todo App Evolution. The constitution defines 8 core principles:

1. Spec-Driven Development (NON-NEGOTIABLE) - All code must be generated via Claude Code from specifications. Manual coding is prohibited. The workflow follows: spec -> plan -> tasks -> implement.

2. Phase-Based Evolution - 5 phases in strict order: Console (Python CLI) -> Web (Next.js + FastAPI) -> Chatbot (OpenAI ChatKit + Agents SDK) -> Local K8s (Docker + Minikube) -> Cloud (Kafka + Dapr).

3. Monorepo Organization - Single repository with frontend/backend separation: backend/, frontend/, infra/, specs/.

4. Clean Code Standards - Descriptive names, docstrings, proper structure, type hints required. Linting and formatting tools mandatory.

5. WSL 2 for Windows - All development commands execute within WSL 2.

6. Security & Secrets - Environment variables, no hardcoded credentials, JWT tokens for auth.

7. AI-First Development - OpenAI Agents SDK, MCP tools, stateless chat endpoints, PHRs for traceability.

8. Cloud-Native Architecture - Docker, Kubernetes, Kafka, Dapr, Helm charts.

Technology stack specified per phase with version requirements. Constraints include no manual coding, sequential phases, 90-second demo videos. Governance defines amendment procedure and compliance review.

## Outcome

- Impact: Established foundational project governance with clear principles and constraints for hackathon development
- Tests: None (constitution document)
- Files: 1 created (constitution.md)
- Next prompts: Consider creating first feature spec for Phase I console application
- Reflection: Initial constitution captures all user requirements with clear structure. Templates may need minor updates to align with phase-based workflow.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Create first feature specification for Phase I console todo app
