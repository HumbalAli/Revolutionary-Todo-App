# Quickstart: Advanced Cloud Deployment with Kafka, Dapr, and Event-Driven Architecture

**Feature**: 005-kafka-dapr-architecture
**Date**: 2026-02-07
**Purpose**: Quick reference for developers to understand and work with Phase V implementation

## Overview

Phase V adds advanced task management features with event-driven architecture:
- **Advanced Features**: Recurring tasks, due dates, reminders, priorities, tags, search/filter/sort
- **Event-Driven**: Kafka for event streaming, Dapr for distributed application runtime
- **Cloud-Native**: Deploys to DigitalOcean DOKS, Azure AKS, or Google GKE

## Architecture Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Next.js   │────────▶│   FastAPI    │────────▶│  Neon DB    │
│  Frontend   │   HTTP  │   Backend    │         │ PostgreSQL  │
└─────────────┘         └──────┬───────┘         └─────────────┘
                               │
                               │ Dapr Sidecar
                               │
                        ┌──────▼───────┐
                        │              │
                        │  Pub/Sub     │         ┌─────────────┐
                        │  State Mgmt  │────────▶│   Kafka     │
                        │  Bindings    │         │  (Redpanda) │
                        │  Secrets     │         └─────────────┘
                        │              │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   Consumer   │
                        │   Services   │
                        └──────────────┘
```

## Key Concepts

### 1. Advanced Task Properties

Tasks now support:
- **Due Date**: Timestamp when task should be completed
- **Priority**: HIGH, MEDIUM, LOW
- **Tags**: User-defined categories (e.g., ["work", "urgent"])
- **Recurrence**: RFC 5545 RRule format (e.g., "FREQ=WEEKLY;BYDAY=MO,WE,FR")
- **Reminders**: Notifications before due date

### 2. Event-Driven Flow

**Task Creation Flow**:
1. User creates task via API → Backend validates and stores in DB
2. Backend publishes `task.created` event to Kafka `task-events` topic
3. Audit log consumer records event
4. If recurring, recurring service monitors for completion events

**Reminder Flow**:
1. Dapr cron binding triggers reminder check every minute
2. Backend queries tasks with `due_date <= now() + reminder_offset`
3. Backend publishes `reminder.due` event to Kafka `reminders` topic
4. Reminder consumer sends notification (email/push/WebSocket)
5. Consumer publishes `reminder.sent` event back to Kafka

**Recurring Task Flow**:
1. User completes recurring task via API
2. Backend publishes `task.completed` event to Kafka
3. Recurring service consumes event, parses RRule
4. Service creates next occurrence task
5. Service publishes `task.created` event for new occurrence

### 3. Dapr Building Blocks

**Pub/Sub** (kafka-pubsub component):
- Abstracts Kafka producer/consumer APIs
- Automatic retry, dead-letter queues
- Cloud-agnostic (switch to Azure Service Bus, AWS SQS easily)

**State Management** (statestore component):
- Stores conversation context for AI assistant
- TTL for automatic expiration
- Strong consistency via PostgreSQL backend

**Service Invocation** (app-id: todo-backend):
- Service discovery without hardcoded URLs
- Built-in mTLS, retries, circuit breaking
- Observability via Dapr telemetry

**Bindings** (reminder-cron):
- Cron trigger for scheduled jobs
- Decouples scheduling from application code

**Secrets Management** (kubernetes-secrets):
- Secure credential access
- Rotates secrets without application restart

## Development Workflow

### Prerequisites

- Docker Desktop (with Kubernetes enabled) or Minikube
- Dapr CLI installed: `wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash`
- kubectl configured for local cluster
- Helm 3.x installed

### Local Setup (Minikube + Strimzi)

**1. Start Minikube**:
```bash
minikube start --memory=8192 --cpus=4
minikube addons enable ingress
```

**2. Install Dapr**:
```bash
dapr init --kubernetes --wait
kubectl get pods -n dapr-system  # Verify Dapr is running
```

**3. Install Strimzi Kafka**:
```bash
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f infra/kafka/strimzi/kafka-cluster.yaml -n kafka
kubectl wait kafka/my-cluster --for=condition=Ready --timeout=300s -n kafka
```

**4. Create Kafka Topics**:
```bash
kubectl apply -f infra/kafka/strimzi/kafka-topics.yaml -n kafka
```

**5. Deploy Application**:
```bash
helm install todo-chatbot infra/helm/todo-chatbot \
  --set kafka.brokers="my-cluster-kafka-bootstrap.kafka.svc:9092" \
  --set database.url="postgresql://user:pass@neon.tech/db" \
  --set openai.apiKey="sk-..." \
  --namespace default
```

**6. Verify Deployment**:
```bash
kubectl get pods  # Should see backend and frontend pods with Dapr sidecars
kubectl logs -l app=todo-backend -c daprd  # Check Dapr sidecar logs
kubectl port-forward svc/todo-frontend 3000:3000
```

Access application at: http://localhost:3000

### Cloud Deployment (DigitalOcean + Redpanda Cloud)

**1. Create Kubernetes Cluster**:
```bash
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3"
```

**2. Configure kubectl**:
```bash
doctl kubernetes cluster kubeconfig save todo-cluster
```

**3. Install Dapr**:
```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm install dapr dapr/dapr --namespace dapr-system --create-namespace --wait
```

**4. Create Redpanda Cloud Instance**:
- Sign up at https://redpanda.com/try-redpanda
- Create cluster, note bootstrap servers and credentials
- Create topics: `task-events`, `reminders`, `task-updates`

**5. Create Kubernetes Secrets**:
```bash
kubectl create secret generic app-secrets \
  --from-literal=database-url="postgresql://user:pass@neon.tech/db" \
  --from-literal=kafka-brokers="redpanda.example.com:9092" \
  --from-literal=kafka-username="user" \
  --from-literal=kafka-password="pass" \
  --from-literal=openai-api-key="sk-..." \
  --from-literal=jwt-secret="your-secret"
```

**6. Deploy Application**:
```bash
helm install todo-chatbot infra/helm/todo-chatbot \
  --set kafka.enabled=true \
  --set kafka.brokers="redpanda.example.com:9092" \
  --set kafka.authType="password" \
  --set ingress.enabled=true \
  --set ingress.host="todo-app.example.com" \
  --namespace default
```

**7. Get LoadBalancer IP**:
```bash
kubectl get svc todo-frontend
# Configure DNS A record: todo-app.example.com → LoadBalancer IP
```

Access application at: https://todo-app.example.com

## API Examples

### Create Task with Advanced Properties

```bash
curl -X POST http://localhost:8000/api/v2/tasks \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly team standup",
    "description": "Review progress and blockers",
    "due_date": "2026-02-10T10:00:00Z",
    "priority": "HIGH",
    "tags": ["work", "meeting"],
    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
    "reminder_offset_minutes": 30
  }'
```

### Search and Filter Tasks

```bash
curl -X GET "http://localhost:8000/api/v2/tasks?search=standup&priority=HIGH&tags=work&sort_by=due_date&sort_order=asc" \
  -H "Authorization: Bearer <jwt_token>"
```

### Complete Task (triggers next occurrence)

```bash
curl -X POST http://localhost:8000/api/v2/tasks/{task_id}/complete \
  -H "Authorization: Bearer <jwt_token>"
```

Response includes next occurrence if recurring:
```json
{
  "completed_task": { "id": "...", "status": "completed" },
  "next_occurrence": { "id": "...", "due_date": "2026-02-17T10:00:00Z" }
}
```

## Kafka Event Inspection

### View Task Events

```bash
# Local (Strimzi)
kubectl run kafka-consumer -ti --image=quay.io/strimzi/kafka:latest-kafka-3.6.0 --rm=true --restart=Never -- \
  bin/kafka-console-consumer.sh --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc:9092 --topic task-events --from-beginning

# Cloud (Redpanda)
rpk topic consume task-events --brokers redpanda.example.com:9092
```

### Produce Test Event

```bash
kubectl run kafka-producer -ti --image=quay.io/strimzi/kafka:latest-kafka-3.6.0 --rm=true --restart=Never -- \
  bin/kafka-console-producer.sh --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc:9092 --topic reminders

# Type JSON event:
{"event_type":"reminder.due","schema_version":"1.0","timestamp":"2026-02-07T12:00:00Z","user_id":"test-user","task_id":"test-task","reminder_id":"test-reminder","data":{"task_title":"Test","due_date":"2026-02-07T13:00:00Z","scheduled_time":"2026-02-07T12:00:00Z","delivery_method":"EMAIL"}}
```

## Troubleshooting

### Dapr Sidecar Not Starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c daprd
```

Common issues:
- Missing Dapr annotations on deployment
- Component configuration errors
- Resource limits too low for sidecar

### Kafka Connection Issues

```bash
# Test Kafka connectivity from pod
kubectl exec -it <backend-pod> -c todo-backend -- \
  curl -v telnet://my-cluster-kafka-bootstrap.kafka.svc:9092
```

Verify:
- Kafka brokers are running: `kubectl get pods -n kafka`
- Topics exist: `kubectl get kafkatopics -n kafka`
- Network policies allow communication

### Reminder Not Sending

Check:
1. Cron binding triggering: `kubectl logs <backend-pod> -c daprd | grep cron`
2. Events published to `reminders` topic: (see Kafka inspection above)
3. Reminder consumer running: `kubectl get pods -l app=reminder-consumer`
4. Consumer logs: `kubectl logs -l app=reminder-consumer`

### Database Migration Issues

```bash
# Check migration job status
kubectl get jobs
kubectl logs job/db-migration

# Manually run migration
kubectl exec -it <backend-pod> -c todo-backend -- \
  alembic upgrade head
```

## Performance Testing

### Load Test Search/Filter (SC-004: <2s for 10K tasks)

```bash
# Seed 10K tasks
python scripts/seed_tasks.py --count 10000

# Run load test
k6 run tests/load/search-filter.js
```

### Verify Kafka Delivery Rate (SC-007: 99.9% delivery)

```bash
# Monitor Kafka consumer lag
kubectl exec -it deployment/todo-backend -c daprd -- \
  curl http://localhost:3500/v1.0/metadata | jq '.subscriptions'

# Check consumer offset lag
kubectl run kafka-consumer-groups -ti --image=quay.io/strimzi/kafka:latest-kafka-3.6.0 --rm=true --restart=Never -- \
  bin/kafka-consumer-groups.sh --bootstrap-server my-cluster-kafka-bootstrap.kafka.svc:9092 --describe --group todo-app-backend
```

## Next Steps

1. Review [plan.md](./plan.md) for implementation details
2. Review [data-model.md](./data-model.md) for entity schemas
3. Review [contracts/](./contracts/) for API and event specifications
4. Run `/sp.tasks` to generate implementation tasks
5. Execute tasks via `/sp.implement`

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Strimzi Kafka Operator](https://strimzi.io/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [RFC 5545 RRule Specification](https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html)
- [DigitalOcean Kubernetes](https://docs.digitalocean.com/products/kubernetes/)
- [Azure AKS](https://docs.microsoft.com/en-us/azure/aks/)
- [Google GKE](https://cloud.google.com/kubernetes-engine/docs)