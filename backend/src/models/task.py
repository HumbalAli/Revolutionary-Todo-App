from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from .user import User


class TaskBase(SQLModel):
    title: str = Field(nullable=False, min_length=1, max_length=255)
    description: Optional[str] = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)


class Task(TaskBase, table=True):
    """
    Task model representing a todo item with core attributes and relationships.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to User
    user: Optional[User] = Relationship(back_populates="tasks")


# Add the tasks relationship to User model
User.model_rebuild()