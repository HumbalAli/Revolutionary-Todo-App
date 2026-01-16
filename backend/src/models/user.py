from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)
    name: str = Field(nullable=False, max_length=255)


class User(UserBase, table=True):
    """
    User model representing an authenticated user with associated tasks.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tasks: List["Task"] = Relationship(back_populates="user")


# Add the tasks relationship to Task model (after both classes are defined to handle circular import)
def model_rebuild():
    from backend.src.models.task import Task
    User.__annotations__['tasks'] = List["Task"]
    User.tasks = Relationship(back_populates="user")