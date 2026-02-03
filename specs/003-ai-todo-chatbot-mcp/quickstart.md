# Quickstart Guide: AI-Powered Todo Chatbot

## Prerequisites

- Node.js 18+ with npm/yarn
- Python 3.11+ with pip
- OpenAI API key
- MCP SDK access
- Git

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd todo-app
```

### 2. Set Up Backend
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and database connection
```

### 3. Set Up Frontend
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API URLs and other configuration
```

### 4. Environment Variables

#### Backend (.env)
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
BETTER_AUTH_SECRET=your_better_auth_secret
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_api_key_here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

## Running the Application

### 1. Start the Backend
```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

### 3. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs

## Key Features

### Chat Interface
- Natural language task management
- Commands like "Add a task to buy groceries"
- "Show me pending tasks", "Mark task as complete"
- "Delete task", "Update task description"

### Task Operations via Chat
- **Add Task**: "Add a task to {title}" or "Create task {title}"
- **List Tasks**: "Show my tasks", "What do I have to do?"
- **Complete Task**: "Mark {task} as done", "Complete task {id}"
- **Delete Task**: "Remove task {title}", "Delete task {id}"
- **Update Task**: "Change task {title} to {new_title}"

### Authentication
- Integrated with Better Auth system
- User sessions maintained across chat interactions
- Secure API communication

## Development Workflow

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm run test
```

### Building for Production
```bash
# Frontend build
cd frontend
npm run build

# Backend build (if using containerization)
cd backend
docker build -t todo-backend .
```

## Troubleshooting

### Common Issues

1. **API Keys Not Working**
   - Verify environment variables are set correctly
   - Check OpenAI API key has proper permissions
   - Ensure MCP SDK is properly configured

2. **Database Connection Issues**
   - Verify DATABASE_URL is correct
   - Check database is running and accessible
   - Ensure Neon PostgreSQL connection pooling is configured properly

3. **Chat Interface Not Responding**
   - Check that backend is running
   - Verify API endpoints are accessible
   - Check browser console for errors

### Debugging Commands
```bash
# Check backend health
curl http://localhost:8000/health

# Check API connectivity
curl http://localhost:8000/api/tasks

# View logs
tail -f logs/app.log
```

## Architecture Overview

### Backend Structure
```
backend/
├── src/
│   ├── main.py          # FastAPI application entrypoint
│   ├── database.py      # Database connection and models
│   ├── auth.py          # Authentication utilities
│   └── api/
│       └── routes/
│           ├── tasks.py # Task-related endpoints
│           └── auth.py  # Authentication endpoints
├── requirements.txt     # Python dependencies
└── alembic/            # Database migrations
```

### Frontend Structure
```
frontend/
├── src/
│   ├── pages/           # Next.js pages
│   │   └── index.tsx    # Main application page
│   ├── components/      # React components
│   │   ├── TaskForm.tsx
│   │   ├── TaskList.tsx
│   │   └── ChatInterface.tsx
│   ├── services/        # API services
│   │   └── api.ts       # API client
│   └── types/           # TypeScript type definitions
├── package.json         # Node.js dependencies
└── next.config.js       # Next.js configuration
```

## MCP Tool Integration

The chatbot uses MCP tools for task operations:
- `add_task`: Creates new tasks from natural language
- `list_tasks`: Retrieves tasks with optional filtering
- `complete_task`: Marks tasks as complete
- `delete_task`: Removes tasks
- `update_task`: Modifies task details

These tools are registered with the OpenAI Agents SDK and called when the AI detects appropriate intents in user messages.