# Research Findings: AI-Powered Todo Chatbot with MCP Tools

## MCP Server Integration

### Decision: Use Official MCP SDK with FastAPI
Based on research, the official MCP SDK can be integrated with FastAPI using the following approach:

1. Create a FastAPI application that exposes MCP tool definitions
2. Register task operation functions as MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
3. Use the existing database connection to perform operations

### Rationale
This approach leverages the existing FastAPI backend infrastructure while adding MCP tool functionality. It maintains consistency with the current architecture.

### Alternatives Considered
- Standalone MCP server: Would require additional deployment complexity
- Client-side MCP tools: Would expose database directly to frontend (security concern)

## OpenAI Services Assessment

### Decision: Use GPT-4 Turbo for Optimal Cost/Performance
GPT-4 Turbo offers the best balance of performance and cost for natural language processing tasks. For a todo app chatbot, the intelligence needed is moderate, and GPT-4 Turbo provides reliable intent recognition.

### Rationale
- Better accuracy than GPT-3.5 for understanding varied command phrasings
- More cost-effective than GPT-4 for frequent, smaller interactions
- Adequate intelligence for task management commands

### Estimated Costs
- Expected usage: ~1M tokens/month (conservative estimate)
- Cost: ~$10-15/month at GPT-4 Turbo pricing
- Can optimize with caching and prompt engineering to reduce costs

## Conversation State Management

### Decision: Store Conversation History in Neon PostgreSQL
Conversation state will be stored in the existing Neon database with a new Conversation table that tracks:
- conversation_id (UUID)
- user_id (foreign key to existing users)
- messages (JSONB field with message history)
- context (JSONB field with current conversation context)
- created_at, updated_at timestamps

### Rationale
- Maintains consistency with existing database approach
- Leverages Neon's serverless scaling capabilities
- Ensures data stays within the same security boundary
- Allows for conversation analytics and debugging

### Privacy Considerations
- Implement data retention policies (automatically delete conversations after 90 days)
- Encrypt sensitive message content at application layer
- Provide users ability to delete their conversation history