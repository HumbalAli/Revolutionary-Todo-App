from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.src.database import engine
from backend.src.models import User, Task
import os

from sqlmodel import SQLModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    try:
        SQLModel.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        # Don't raise the exception to prevent blocking startup
    yield

app = FastAPI(
    title="Todo API",
    description="API for managing todo tasks with user authentication",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from backend.src.api.routes import tasks, auth

app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(auth.router, prefix="/api", tags=["auth"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}


@app.get("/")
async def root():
    return {"message": "Welcome to Todo API"}

