"""Data models for the ToDo application"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class TodoStatus(str, Enum):
    """Status of a todo item"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TodoPriority(str, Enum):
    """Priority level of a todo item"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoItem(BaseModel):
    """A single todo item"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "1",
                "title": "Build OpenAI App",
                "description": "Create a todo app using OpenAI Apps SDK",
                "status": "in_progress",
                "priority": "high",
                "tags": ["development", "openai"]
            }
        }
    )

    id: str = Field(..., description="Unique identifier for the todo item")
    title: str = Field(..., description="Title of the todo item")
    description: Optional[str] = Field(None, description="Detailed description")
    status: TodoStatus = Field(default=TodoStatus.PENDING, description="Current status")
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM, description="Priority level")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    due_date: Optional[datetime] = Field(None, description="Due date for the todo")
    tags: list[str] = Field(default_factory=list, description="Tags associated with the todo")


class TodoCreate(BaseModel):
    """Model for creating a new todo item"""
    title: str = Field(..., min_length=1, description="Title of the todo item")
    description: Optional[str] = Field(None, description="Detailed description")
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM, description="Priority level")
    due_date: Optional[datetime] = Field(None, description="Due date for the todo")
    tags: list[str] = Field(default_factory=list, description="Tags associated with the todo")


class TodoUpdate(BaseModel):
    """Model for updating a todo item"""
    title: Optional[str] = Field(None, min_length=1, description="Title of the todo item")
    description: Optional[str] = Field(None, description="Detailed description")
    status: Optional[TodoStatus] = Field(None, description="Current status")
    priority: Optional[TodoPriority] = Field(None, description="Priority level")
    due_date: Optional[datetime] = Field(None, description="Due date for the todo")
    tags: Optional[list[str]] = Field(None, description="Tags associated with the todo")
