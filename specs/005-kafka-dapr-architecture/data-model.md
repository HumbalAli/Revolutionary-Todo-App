# Data Model: Advanced Cloud Deployment with Kafka, Dapr, and Event-Driven Architecture

**Feature**: 005-kafka-dapr-architecture
**Date**: 2026-02-07
**Purpose**: Define data entities, relationships, and schemas for Phase V implementation

## Entity Overview

This phase extends the existing Task entity and introduces new entities for advanced features:

1. **AdvancedTask** (extends existing Task)
2. **RecurringRule** (new)
3. **TaskEvent** (new)
4. **Reminder** (new)
5. **UserProfile** (new)

## Entity Definitions

### 1. AdvancedTask

Extends the existing `Task` entity with advanced properties for Phase V.

**Fields**:
- `id`: UUID (primary key, inherited)
- `user_id`: UUID (foreign key, inherited)
- `title`: String (inherited)
- `description`: String (inherited)
- `status`: Enum (inherited: pending, in_progress, completed)
- `created_at`: Timestamp (inherited)
- `updated_at`: Timestamp (inherited)
- **`due_date`**: Timestamp (nullable) - When task is due
- **`priority`**: Enum (nullable) - HIGH, MEDIUM, LOW
- **`tags`**: Array<String> (nullable) - User-defined tags (e.g., ["work", "urgent"])
- **`recurrence_rule`**: String (nullable) - RFC 5545 RRule format
- **`recurrence_parent_id`**: UUID (nullable) - Links to original recurring task
- **`reminder_offset_minutes`**: Integer (nullable) - Minutes before due_date to send reminder (default: 60)
- **`is_recurring`**: Boolean (default: false) - Whether this is a recurring task
- **`recurrence_count`**: Integer (nullable) - Current occurrence number (1, 2, 3...)

**Relationships**:
- `user_id` → User (many-to-one)
- `recurrence_parent_id` → AdvancedTask (self-referential, one-to-many)

**Indexes**:
- Primary: `id`
- Foreign key: `user_id`, `recurrence_parent_id`
- Search: GIN index on `search_vector` (tsvector of title + description)
- Filter: B-tree on `priority`, `status`, `due_date`
- Tags: GIN index on `tags` array

**Validation Rules**:
- `due_date` must be in the future for new tasks
- `priority` must be one of HIGH, MEDIUM, LOW if provided
- `recurrence_rule` must be valid RRule format if provided
- `is_recurring` must be true if `recurrence_rule` is set
- `reminder_offset_minutes` must be positive if provided

**State Transitions**:
- `pending` → `in_progress` → `completed`
- Completing a recurring task (is_recurring=true) triggers creation of next occurrence

---

### 2. RecurringRule

Stores parsed recurrence metadata for efficient querying and display.

**Fields**:
- `id`: UUID (primary key)
- `task_id`: UUID (foreign key to AdvancedTask)
- `rrule_string`: String - Full RRule string (e.g., "FREQ=WEEKLY;BYDAY=MO,WE,FR")
- `frequency`: Enum - DAILY, WEEKLY, MONTHLY, YEARLY
- `interval`: Integer - Every N days/weeks/months/years
- `by_day`: Array<String> (nullable) - Days of week (e.g., ["MO", "WE", "FR"])
- `by_month_day`: Array<Integer> (nullable) - Days of month (e.g., [1, 15])
- `count`: Integer (nullable) - Total occurrences (null for infinite)
- `until`: Timestamp (nullable) - End date for recurrence
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Relationships**:
- `task_id` → AdvancedTask (one-to-one)

**Indexes**:
- Primary: `id`
- Unique: `task_id`

**Validation Rules**:
- `frequency` must be one of DAILY, WEEKLY, MONTHLY, YEARLY
- `interval` must be positive integer
- `count` and `until` are mutually exclusive (can't both be set)
- If `frequency=WEEKLY`, `by_day` is recommended
- If `frequency=MONTHLY`, `by_month_day` is recommended

---

### 3. TaskEvent

Represents events published to Kafka for audit log and triggering downstream actions.

**Fields**:
- `id`: UUID (primary key)
- `event_type`: String - e.g., "task.created", "task.completed", "task.deleted"
- `schema_version`: String - Event schema version (e.g., "1.0")
- `timestamp`: Timestamp - When event occurred
- `user_id`: UUID - User who triggered the event
- `task_id`: UUID - Task related to event
- `data`: JSONB - Event-specific payload
- `kafka_partition`: Integer (nullable) - Kafka partition where event was published
- `kafka_offset`: Integer (nullable) - Kafka offset of event

**Relationships**:
- `user_id` → User (many-to-one)
- `task_id` → AdvancedTask (many-to-one)

**Indexes**:
- Primary: `id`
- Query: Composite index on `(user_id, timestamp DESC)` for audit log queries
- Lookup: Index on `task_id` for task history

**Validation Rules**:
- `event_type` must follow pattern "entity.action" (e.g., "task.created")
- `schema_version` must match supported versions
- `timestamp` must not be in the future

**Event Types**:
- `task.created`: New task created
- `task.updated`: Task properties changed
- `task.completed`: Task marked complete
- `task.deleted`: Task deleted
- `task.priority_changed`: Priority modified
- `task.due_date_changed`: Due date modified
- `task.recurrence_updated`: Recurrence rule changed

---

### 4. Reminder

Tracks reminder state to ensure idempotent delivery and audit trail.

**Fields**:
- `id`: UUID (primary key)
- `task_id`: UUID (foreign key to AdvancedTask)
- `user_id`: UUID (foreign key to User)
- `scheduled_time`: Timestamp - When reminder should be sent
- `sent_at`: Timestamp (nullable) - When reminder was actually sent
- `status`: Enum - PENDING, SENT, FAILED, CANCELLED
- `delivery_method`: Enum - EMAIL, PUSH, WEBSOCKET (future extension)
- `retry_count`: Integer (default: 0) - Number of delivery attempts
- `error_message`: String (nullable) - Error details if status=FAILED
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Relationships**:
- `task_id` → AdvancedTask (many-to-one)
- `user_id` → User (many-to-one)

**Indexes**:
- Primary: `id`
- Query: Composite index on `(scheduled_time, status)` for cron job queries
- Lookup: Index on `task_id` for task-reminder relationship

**Validation Rules**:
- `scheduled_time` must be before task's `due_date`
- `status` must transition: PENDING → SENT|FAILED|CANCELLED
- `sent_at` must be null when status=PENDING
- `retry_count` must not exceed 3

**State Transitions**:
- `PENDING` → `SENT` (successful delivery)
- `PENDING` → `FAILED` (delivery failure, retry if retry_count < 3)
- `PENDING` → `CANCELLED` (task completed before reminder sent)

---

### 5. UserProfile

Stores user-specific preferences for advanced features.

**Fields**:
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to User, unique)
- `default_priority`: Enum (nullable) - HIGH, MEDIUM, LOW
- `default_reminder_offset_minutes`: Integer (default: 60) - Default reminder time
- `default_tags`: Array<String> (default: []) - Suggested tags
- `notification_preferences`: JSONB - Delivery method preferences
- `timezone`: String (default: "UTC") - User's timezone for due dates
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Relationships**:
- `user_id` → User (one-to-one)

**Indexes**:
- Primary: `id`
- Unique: `user_id`

**Validation Rules**:
- `default_priority` must be one of HIGH, MEDIUM, LOW if provided
- `default_reminder_offset_minutes` must be positive
- `timezone` must be valid IANA timezone identifier

---

## Relationships Diagram

```
User (existing)
  ├─→ AdvancedTask (1:N)
  │     ├─→ RecurringRule (1:1)
  │     ├─→ TaskEvent (1:N)
  │     └─→ Reminder (1:N)
  └─→ UserProfile (1:1)

AdvancedTask
  └─→ AdvancedTask (self-referential for recurrence parent)
```

## Database Schema Changes

### New Tables

1. **recurring_rules** (new table)
2. **task_events** (new table)
3. **reminders** (new table)
4. **user_profiles** (new table)

### Modified Tables

1. **tasks** → **advanced_tasks** (add columns):
   - `due_date` TIMESTAMP NULL
   - `priority` VARCHAR(10) NULL CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW'))
   - `tags` TEXT[] DEFAULT '{}'
   - `recurrence_rule` TEXT NULL
   - `recurrence_parent_id` UUID NULL REFERENCES advanced_tasks(id)
   - `reminder_offset_minutes` INTEGER NULL CHECK (reminder_offset_minutes > 0)
   - `is_recurring` BOOLEAN DEFAULT FALSE
   - `recurrence_count` INTEGER NULL
   - `search_vector` TSVECTOR

### Indexes to Create

```sql
-- Full-text search on tasks
CREATE INDEX idx_tasks_search_vector ON advanced_tasks USING GIN(search_vector);

-- Filter/sort indexes
CREATE INDEX idx_tasks_due_date ON advanced_tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON advanced_tasks(priority) WHERE priority IS NOT NULL;
CREATE INDEX idx_tasks_tags ON advanced_tasks USING GIN(tags);

-- Reminder queries
CREATE INDEX idx_reminders_scheduled ON reminders(scheduled_time, status) WHERE status = 'PENDING';

-- Event audit log
CREATE INDEX idx_task_events_user_time ON task_events(user_id, timestamp DESC);
```

## Migration Strategy

### Backward Compatibility

- Existing `tasks` table renamed to `advanced_tasks` with new columns (nullable)
- Existing tasks continue to work (null values for new fields)
- API version 2.0 supports new fields, API v1.0 ignores them

### Data Migration Steps

1. Add new columns to tasks table (all nullable to avoid breaking changes)
2. Create new tables (recurring_rules, task_events, reminders, user_profiles)
3. Create indexes
4. Update ORM models to reflect schema changes
5. Deploy new backend with dual API version support
6. Backfill user_profiles with default values for existing users

### Rollback Plan

- New columns are nullable, so rollback removes them without data loss
- New tables can be dropped if no data written
- Old API version continues to work during migration

---

## Kafka Event Schemas

### Topic: task-events

**Event**: task.created

```json
{
  "event_type": "task.created",
  "schema_version": "1.0",
  "timestamp": "2026-02-07T12:00:00Z",
  "user_id": "uuid",
  "task_id": "uuid",
  "data": {
    "title": "string",
    "description": "string",
    "due_date": "ISO8601 timestamp",
    "priority": "HIGH|MEDIUM|LOW",
    "tags": ["string"],
    "is_recurring": true,
    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO,WE,FR"
  }
}
```

### Topic: reminders

**Event**: reminder.due

```json
{
  "event_type": "reminder.due",
  "schema_version": "1.0",
  "timestamp": "2026-02-07T12:00:00Z",
  "user_id": "uuid",
  "task_id": "uuid",
  "reminder_id": "uuid",
  "data": {
    "task_title": "string",
    "due_date": "ISO8601 timestamp",
    "scheduled_time": "ISO8601 timestamp",
    "delivery_method": "EMAIL|PUSH|WEBSOCKET"
  }
}
```

### Topic: task-updates

**Event**: task.priority_changed

```json
{
  "event_type": "task.priority_changed",
  "schema_version": "1.0",
  "timestamp": "2026-02-07T12:00:00Z",
  "user_id": "uuid",
  "task_id": "uuid",
  "data": {
    "old_priority": "MEDIUM",
    "new_priority": "HIGH"
  }
}
```

## Dapr State Store Schema

### Key Format

`conversation-state:{user_id}:{session_id}`

### Value Schema

```json
{
  "user_id": "uuid",
  "session_id": "uuid",
  "last_activity": "ISO8601 timestamp",
  "context": {
    "active_filters": {
      "priority": ["HIGH", "MEDIUM"],
      "tags": ["work"],
      "status": ["pending"]
    },
    "last_query": "string",
    "conversation_history": [
      {
        "role": "user|assistant",
        "content": "string",
        "timestamp": "ISO8601 timestamp"
      }
    ]
  }
}
```

**TTL**: 1 hour (configured via Dapr component metadata)

---

## Summary

This data model extends the existing Phase II-IV schema with:
- 8 new fields on AdvancedTask entity
- 4 new entities (RecurringRule, TaskEvent, Reminder, UserProfile)
- 3 Kafka event schemas
- Dapr state schema for conversation context
- Backward-compatible migration strategy
- Comprehensive indexes for performance (meets SC-004: <2s search for 10K tasks)