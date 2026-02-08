# Research: Advanced Cloud Deployment with Kafka, Dapr, and Event-Driven Architecture

**Feature**: 005-kafka-dapr-architecture
**Date**: 2026-02-07
**Purpose**: Resolve technical unknowns and establish best practices for Phase V implementation

## Research Questions

### 1. Kafka Deployment Strategy: Strimzi vs Redpanda

**Decision**: Use Redpanda for cloud deployment, Strimzi for local Minikube

**Rationale**:
- **Redpanda** (cloud): Kafka-compatible, lower resource requirements, simpler operations, better for managed cloud environments. Redpanda Cloud offers fully managed service with better economics than self-hosting Kafka.
- **Strimzi** (local): Kubernetes-native Kafka operator, excellent for local development on Minikube, provides full Kafka ecosystem compatibility for testing.

**Alternatives Considered**:
- **Confluent Cloud**: More expensive, vendor lock-in, overkill for hackathon scope
- **Vanilla Kafka on K8s**: Complex to operate, requires ZooKeeper management
- **AWS MSK/Azure Event Hubs**: Cloud-specific, reduces portability

**Implementation Notes**:
- Use Kafka protocol for both (ensures portability)
- Topics: `task-events`, `reminders`, `task-updates`
- Partition strategy: Key by user_id for ordering guarantees
- Retention: 7 days for events, 1 day for reminders

---

### 2. Dapr State Store Backend

**Decision**: Use existing PostgreSQL (Neon) as Dapr state store for conversation state

**Rationale**:
- Reuses existing database infrastructure
- Strong consistency guarantees for conversation state
- Simplified operations (no additional database)
- Neon's serverless architecture handles variable load

**Alternatives Considered**:
- **Redis**: Faster but adds operational complexity, eventual consistency issues
- **DynamoDB/CosmosDB**: Cloud-specific, additional cost
- **etcd**: Overkill for state management needs

**Implementation Notes**:
- Configure Dapr PostgreSQL state store component
- Use separate schema/tables for Dapr state to avoid conflicts
- Enable Dapr state store encryption
- TTL configured via Dapr component metadata

---

### 3. Recurring Task Pattern: Cron vs RRule

**Decision**: Use RFC 5545 RRule standard for recurrence patterns

**Rationale**:
- Industry standard (iCalendar specification)
- Rich expressiveness (daily, weekly, monthly, yearly with exceptions)
- Well-supported libraries: `python-dateutil` (backend), `rrule.js` (frontend)
- Human-readable format for debugging

**Alternatives Considered**:
- **Cron expressions**: Less expressive, no exception dates, server-oriented
- **Custom DSL**: Reinventing the wheel, maintenance burden

**Implementation Notes**:
- Store RRule string in database alongside task
- Parse with `dateutil.rrule` to compute next occurrence
- UI provides presets (daily, weekly, monthly) and custom RRule builder
- Example: `FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=10`

---

### 4. Reminder Delivery Mechanism

**Decision**: Dapr Cron Binding + Kafka reminder topic

**Rationale**:
- **Dapr Cron Binding**: Triggers periodic check for due reminders (every 1 minute)
- **Kafka `reminders` topic**: Decouples reminder generation from delivery
- **Consumer-based delivery**: Separate reminder consumer handles notification dispatch
- Scalable: Multiple consumers for high throughput
- Resilient: Kafka persistence ensures no lost reminders

**Alternatives Considered**:
- **Database polling**: Higher database load, less efficient
- **APScheduler**: Not cloud-native, process-bound
- **Celery Beat**: Additional infrastructure (Redis), operational complexity

**Implementation Notes**:
- Cron binding runs every minute, queries tasks with `due_date <= now() + 5min`
- Publishes reminder events to Kafka
- Reminder consumer sends notifications (email, push, or WebSocket)
- Idempotency: Track sent reminders to avoid duplicates

---

### 5. Dapr Service Invocation vs Direct HTTP

**Decision**: Use Dapr service invocation for backend-to-backend, keep direct HTTP for frontend-to-backend

**Rationale**:
- **Service-to-service**: Dapr provides service discovery, mTLS, retries, circuit breaking
- **Frontend-to-backend**: Keep existing Next.js SSR/API routes for simplicity
- Dapr sidecar only on backend pods

**Alternatives Considered**:
- **Full Dapr everywhere**: Adds complexity to frontend, unnecessary for SSR
- **No Dapr service invocation**: Loses resilience patterns and observability

**Implementation Notes**:
- Dapr app-id: `todo-backend`
- Service invocation endpoint: `http://localhost:3500/v1.0/invoke/todo-backend/method/<endpoint>`
- Frontend continues using standard HTTP to backend service

---

### 6. Cloud Kubernetes Provider Selection

**Decision**: Support multi-cloud with DigitalOcean DOKS as primary, Azure AKS and Google GKE as alternatives

**Rationale**:
- **DigitalOcean DOKS**: Simplest, lowest cost, managed Kubernetes with good hackathon economics
- **Azure AKS**: Free control plane, good integration with Azure services if needed
- **Google GKE**: Industry standard, excellent Kubernetes experience

**Alternatives Considered**:
- **AWS EKS**: More expensive control plane, complex IAM
- **Oracle OKE**: Less mature ecosystem

**Implementation Notes**:
- Use Helm charts for deployment (cloud-agnostic)
- Provide deployment guides for all three providers
- Use Kubernetes secrets for cloud-specific credentials
- LoadBalancer service type for ingress (works across all providers)

---

### 7. Search/Filter Implementation Strategy

**Decision**: PostgreSQL full-text search with GIN index for keyword search, standard indexes for filters

**Rationale**:
- **Full-text search**: Built into PostgreSQL, no additional infrastructure
- **Performance**: GIN indexes provide fast text search on title/description
- **Filter/Sort**: Standard B-tree indexes on priority, due_date, status, tags (array column)
- Meets SC-004 requirement (<2s for 10K tasks)

**Alternatives Considered**:
- **Elasticsearch**: Overkill for scope, operational complexity
- **pg_trgm**: Less accurate for multi-word queries

**Implementation Notes**:
- Create tsvector column for searchable text
- GIN index on tsvector for full-text search
- GIN index on tags array (using array operators)
- B-tree indexes on due_date, priority, status
- Query: `WHERE search_vector @@ plainto_tsquery('english', ?)`

---

### 8. Event Schema Design

**Decision**: Use JSON schemas with versioning for Kafka event payloads

**Rationale**:
- **JSON**: Human-readable, widely supported, flexible for evolution
- **Versioning**: Include schema_version in every event for backward compatibility
- **Schema registry**: Document in contracts/ but skip Confluent Schema Registry (overkill)

**Event Types**:
- **task-events**: `task.created`, `task.updated`, `task.completed`, `task.deleted`
- **reminders**: `reminder.due`, `reminder.sent`
- **task-updates**: `task.priority_changed`, `task.due_date_changed`, `task.recurrence_updated`

**Example Schema**:
```json
{
  "event_type": "task.created",
  "schema_version": "1.0",
  "timestamp": "2026-02-07T12:00:00Z",
  "user_id": "user123",
  "task_id": "task456",
  "data": {
    "title": "Complete hackathon",
    "priority": "high",
    "due_date": "2026-02-28T23:59:59Z",
    "tags": ["hackathon", "urgent"]
  }
}
```

---

### 9. CI/CD Pipeline with GitHub Actions

**Decision**: GitHub Actions workflow for build, test, deploy

**Rationale**:
- **Native GitHub integration**: Already using GitHub for repository
- **Free for public repos**: No cost for hackathon
- **Cloud provider flexibility**: Can deploy to any K8s cluster with kubectl

**Pipeline Stages**:
1. **Build**: Docker images for backend/frontend
2. **Test**: Run pytest (backend), Playwright (frontend)
3. **Push**: Push images to registry (Docker Hub or cloud registry)
4. **Deploy**: Helm upgrade on target K8s cluster

**Implementation Notes**:
- Use GitHub secrets for registry credentials, K8s config
- Trigger on push to main branch
- Tag images with git commit SHA for traceability

---

### 10. Zero-Downtime Deployment Strategy

**Decision**: Kubernetes rolling updates with readiness probes and PodDisruptionBudget

**Rationale**:
- **Rolling update**: Default Kubernetes strategy, gradually replaces pods
- **Readiness probes**: Ensure new pods are ready before routing traffic
- **PodDisruptionBudget**: Prevents all pods from being down during updates
- **Database migrations**: Run as Kubernetes Job before deployment

**Implementation Notes**:
- Set `maxUnavailable: 1` and `maxSurge: 1` for controlled rollout
- Readiness probe: `GET /health` endpoint (checks DB, Kafka, Dapr)
- PodDisruptionBudget: `minAvailable: 1`
- Migration job: Alembic upgrade head before Helm upgrade

---

## Summary of Technical Decisions

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Event Streaming (Cloud) | Redpanda Cloud | Lower cost, simpler operations, Kafka-compatible |
| Event Streaming (Local) | Strimzi on Minikube | Full Kafka ecosystem, local development |
| Dapr State Store | PostgreSQL (Neon) | Reuse existing DB, strong consistency |
| Recurrence Pattern | RFC 5545 RRule | Industry standard, rich expressiveness |
| Reminder Trigger | Dapr Cron Binding | Cloud-native, reliable scheduling |
| Search | PostgreSQL FTS + GIN index | Built-in, no additional infrastructure |
| Cloud K8s Provider | DigitalOcean DOKS (primary) | Lowest cost, simplest for hackathon |
| CI/CD | GitHub Actions | Native integration, free for public repos |
| Deployment Strategy | Rolling updates + readiness | Zero-downtime, Kubernetes-native |

## Next Steps

1. **Phase 1**: Generate data-model.md with entity schemas
2. **Phase 1**: Create API contracts in contracts/ directory
3. **Phase 1**: Update agent context with new technologies
4. **Phase 2**: Generate tasks.md for implementation (/sp.tasks)
