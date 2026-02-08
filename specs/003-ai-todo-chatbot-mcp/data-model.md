# Data Model: AI-Powered Todo Chatbot

## Conversation Entity

### Fields
- `id`: UUID (Primary Key) - Unique identifier for conversation
- `user_id`: Integer (Foreign Key) - Reference to user who owns conversation
- `title`: String - Auto-generated title based on first message or purpose
- `created_at`: DateTime - Timestamp of conversation creation
- `updated_at`: DateTime - Timestamp of last message/activity
- `status`: Enum (active, archived) - Current state of conversation

### Relationships
- One-to-many with User (belongs to user)
- One-to-many with Message (has many messages)

### Validation Rules
- `user_id` must reference existing user
- `title` max length 255 characters
- `status` must be one of allowed values

## Message Entity

### Fields
- `id`: UUID (Primary Key) - Unique identifier for message
- `conversation_id`: UUID (Foreign Key) - Reference to parent conversation
- `sender`: Enum (user, ai) - Indicates message origin
- `content`: Text - The actual message content
- `role`: Enum (user, assistant, system) - Role in conversation (for AI context)
- `created_at`: DateTime - Timestamp of message creation
- `metadata`: JSON - Additional data for AI context (intent, entities, etc.)

### Relationships
- Many-to-one with Conversation (belongs to conversation)

### Validation Rules
- `conversation_id` must reference existing conversation
- `sender` and `role` must be one of allowed values
- `content` required, max 10000 characters

## TaskOperation Entity (Virtual - MCP Tool Results)

### Fields (Virtual - represented as function parameters/results)
- `operation`: Enum (add, list, complete, delete, update) - Type of task operation
- `task_title`: String - Title of task for add/update operations
- `task_description`: Text - Description of task for add/update operations
- `task_id`: Integer - Reference to task for update/delete/complete operations
- `task_filter`: Enum (all, pending, completed) - Filter for list operations
- `status`: Enum (pending, completed) - Status for update operations

### Validation Rules
- For `add` operations: `task_title` is required
- For `update`, `delete`, `complete`: `task_id` is required
- For `list`: `task_filter` is optional, defaults to "all"

## State Transition Patterns

### Conversation States
- `active` → `archived` (when user archives or after inactivity period)
- `archived` → `active` (when user resumes conversation)

### Message Creation Flow
1. User submits message via chat interface
2. Message entity created with sender=user, role=user
3. AI processes message and determines intent
4. AI generates response and creates message with sender=ai, role=assistant
5. Conversation updated_at timestamp refreshed

## Indexing Strategy

### Conversation Table
- Index on `user_id` for efficient user-specific queries
- Index on `updated_at` for chronological sorting
- Composite index on `(user_id, status)` for user conversation listings

### Message Table
- Index on `conversation_id` for conversation-specific queries
- Index on `created_at` for chronological ordering within conversations
- Composite index on `(conversation_id, created_at)` for efficient conversation history retrieval

## Performance Considerations

### Pagination
- Messages should be paginated (e.g., 20 messages per page) for performance
- Use cursor-based pagination with `created_at` for efficient retrieval

### Caching
- Recent conversations can be cached in-memory (Redis) for faster access
- AI model responses can be cached for identical inputs (with expiration)

## Privacy & Security

### Data Retention
- Automatic deletion of conversations after 90 days of inactivity
- User-initiated deletion of conversations and messages
- Right to be forgotten implementation

### Encryption
- Sensitive message content encrypted at application level
- Database-level encryption for conversation data
- Secure transmission via HTTPS/TLS