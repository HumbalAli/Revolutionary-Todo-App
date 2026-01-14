from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine
from .models.user import User
from .models.task import Task
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    from sqlmodel import SQLModel
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        import logging
        logging.error(f"Failed to create database tables: {e}")
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
from .api.routes import tasks, auth

app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(auth.router, prefix="/api", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Welcome to Todo API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

