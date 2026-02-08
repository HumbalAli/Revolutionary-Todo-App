"""FastAPI application for Todo API with Phase V features.

Phase V Features:
- Advanced task properties (due dates, priorities, tags, recurrence)
- Event-driven architecture with Kafka
- Dapr integration (pub/sub, state, bindings)
- Real-time updates via WebSocket
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine
from .models.todo_models import User, Task
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Starting Todo API with Phase V features...")
    # Don't create tables on startup to prevent blocking
    # Tables will be created when first needed
    yield
    logger.info("Shutting down Todo API...")


app = FastAPI(
    title="Todo API",
    description="API for managing todo tasks with advanced features: due dates, priorities, tags, recurrence, and event-driven architecture",
    version="2.0.0",  # Phase V version
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

# ============================================================================
# Import and include routers
# ============================================================================

# Core API routes
from .api.routes import tasks, auth, chat

app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Phase V: Events API route
try:
    from .api.routes import events
    app.include_router(events.router, prefix="/api", tags=["events"])
    logger.info("Events API route registered")
except ImportError as e:
    logger.warning(f"Events route not available: {e}")

# Phase V: Dapr handlers
try:
    from .api.dapr import pubsub, state, bindings
    app.include_router(pubsub.router, tags=["dapr-pubsub"])
    app.include_router(bindings.router, tags=["dapr-bindings"])
    logger.info("Dapr routes registered")
except ImportError as e:
    logger.warning(f"Dapr routes not available: {e}")


# ============================================================================
# Health and Info endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running",
        "version": "2.0.0",
        "features": {
            "advanced_tasks": True,
            "kafka_events": True,
            "dapr_integration": True,
            "websocket_streaming": True
        }
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Todo API",
        "version": "2.0.0",
        "phase": "V - Kafka, Dapr, Event-Driven Architecture",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Todo API",
        "version": "2.0.0",
        "phase": "V",
        "features": [
            "User authentication",
            "Task CRUD operations",
            "AI chat interface",
            "Advanced task properties (due dates, priorities, tags)",
            "Recurring tasks with RRule support",
            "Search, filter, and sort",
            "Event-driven architecture with Kafka",
            "Dapr integration (pub/sub, state, bindings, secrets)",
            "Real-time updates via WebSocket",
            "Audit logging"
        ],
        "kafka_topics": [
            "task-events",
            "reminders",
            "task-updates"
        ],
        "dapr_components": [
            "kafka-pubsub",
            "statestore",
            "reminder-cron",
            "recurring-task-cron",
            "secrets"
        ]
    }
