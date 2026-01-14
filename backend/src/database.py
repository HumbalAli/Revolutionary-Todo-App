from sqlmodel import create_engine, Session
from sqlalchemy import MetaData
from typing import Generator
from .models.user import User
from .models.task import Task
import os

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

# Create engine with proper connection pooling for Neon
from sqlalchemy.pool import QueuePool
import sys

# Only enable echo in development
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,            # Only enable in development
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=300,      # Recycle connections every 5 minutes
    poolclass=QueuePool,
    pool_size=10,          # Increased pool size for production
    max_overflow=20        # Increased overflow for production
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session