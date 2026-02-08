from sqlmodel import create_engine, Session
from sqlalchemy import MetaData
from typing import Generator
from .models.todo_models import User, Task
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
    pool_size=5,           # Reduced pool size for Railway
    max_overflow=10,       # Reduced overflow for Railway
    pool_timeout=20,       # Add connection timeout
    pool_reset_on_return='commit'  # Reset connection on return
)

def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    with Session(engine) as session:
        yield session


# Session factory for direct session creation (used in Dapr bindings)
def SessionLocal() -> Session:
    """Create a new database session directly.
    
    Use this for contexts where FastAPI dependency injection
    is not available (e.g., Dapr cron bindings).
    Remember to close the session when done.
    """
    return Session(engine)