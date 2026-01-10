# Revolutionary Todo App - Phase II

Full-stack web todo application with multi-user authentication built with Next.js and FastAPI.

## Overview

This application provides a complete todo management solution with:
- User authentication via Better Auth
- Task management with CRUD operations
- Responsive web interface
- JWT-based security
- PostgreSQL database with SQLModel ORM

## Architecture

- **Frontend**: Next.js 16+ with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python 3.13+
- **Database**: Neon Serverless PostgreSQL with SQLModel ORM
- **Authentication**: Better Auth with JWT tokens

## Project Structure

```
todo-app/
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── api/          # API endpoints
│   └── requirements.txt
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Next.js pages
│   │   └── services/     # API services
│   └── package.json
├── specs/                # Specification files
└── docker-compose.yml    # Local development
```

## Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.13+
- Docker and Docker Compose
- npm or yarn

### Local Development

1. Clone the repository
2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
4. Set up environment variables (see .env.example files)
5. Start the development servers:
   ```bash
   # Using Docker Compose
   docker-compose up

   # Or run separately
   # Terminal 1: Start backend
   cd backend
   uvicorn src.main:app --reload

   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

## API Endpoints

- `GET /api/{user_id}/tasks` - List all tasks for user
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

## Deployment

### Frontend
Deploy to Vercel using the standard Next.js deployment process.

### Backend
Self-host the FastAPI application with your preferred hosting provider.

## Environment Variables

### Backend (.env)
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT secret key

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_BETTER_AUTH_URL` - Auth service URL

## Development

### Backend Development
- API endpoints in `src/api/routes/`
- Business logic in `src/services/`
- Database models in `src/models/`

### Frontend Development
- Pages in `src/pages/`
- Components in `src/components/`
- API services in `src/services/`
- TypeScript types in `src/types/`

## Technologies Used

- **Backend**: FastAPI, SQLModel, Pydantic
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Database**: PostgreSQL with Neon
- **Authentication**: Better Auth
- **Deployment**: Vercel (frontend), self-hosted (backend)