# Quickstart Guide: Phase II - Full-Stack Web Todo App

## Prerequisites

- Node.js 18+ for frontend development
- Python 3.13+ for backend development
- PostgreSQL-compatible database (Neon Serverless PostgreSQL recommended)
- Git for version control
- npm or yarn package manager

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Backend Setup

#### Navigate to Backend Directory
```bash
cd backend
```

#### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
# Or if using pyproject.toml:
pip install -e .
```

#### Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
NEON_DATABASE_URL=your-neon-database-url
```

#### Database Setup
```bash
# Run database migrations
alembic upgrade head
```

#### Run Backend Server
```bash
uvicorn src.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

#### Navigate to Frontend Directory
```bash
cd frontend
```

#### Install Dependencies
```bash
npm install
# or
yarn install
```

#### Environment Variables
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

#### Run Development Server
```bash
npm run dev
# or
yarn dev
```

Frontend will be available at `http://localhost:3000`

## API Endpoints

The backend provides the following API endpoints:

- `GET /api/{user_id}/tasks` - List all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks/{id}` - Get task details
- `PUT /api/{user_id}/tasks/{id}` - Update a task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion

## Authentication

The application uses Better Auth for user authentication. Users must be registered and logged in to access task endpoints. JWT tokens are included in the Authorization header for API requests.

## Development

### Backend Development
- API endpoints are defined in `src/api/routes/tasks.py`
- Database models are in `src/models/task.py`
- Business logic is in `src/services/task_service.py`

### Frontend Development
- Main page is in `src/pages/index.tsx`
- Task components are in `src/components/`
- API calls are handled in `src/services/api.ts`
- Authentication is managed in `src/services/auth.ts`

## Testing

### Backend Tests
```bash
# Run backend tests
pytest
```

### Frontend Tests
```bash
# Run frontend tests
npm run test
```

## Deployment

### Frontend
The frontend is designed to be deployed on Vercel. Connect your repository to Vercel and set the environment variables in the Vercel dashboard.

### Backend
The backend can be deployed to any platform that supports Python applications. Ensure environment variables are set correctly and the database connection is configured.