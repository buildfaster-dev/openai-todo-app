"""In-memory storage for todo items"""

from datetime import datetime
from typing import Dict, List, Optional
from .models import TodoItem, TodoCreate, TodoUpdate, TodoStatus
import uuid


class TodoStorage:
    """Simple in-memory storage for todo items"""

    def __init__(self):
        self._todos: Dict[str, TodoItem] = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Add some sample todos for demonstration"""
        sample_todos = [
            TodoCreate(
                title="Set up development environment",
                description="Install Nix, uv, and configure the project",
                priority="high",
                tags=["setup", "development"]
            ),
            TodoCreate(
                title="Implement MCP server",
                description="Create FastAPI server with MCP endpoints",
                priority="high",
                tags=["backend", "mcp"]
            ),
            TodoCreate(
                title="Build UI components",
                description="Create the web interface for the todo app",
                priority="medium",
                tags=["frontend", "ui"]
            ),
        ]

        for todo_create in sample_todos:
            self.create(todo_create)

    def create(self, todo_create: TodoCreate) -> TodoItem:
        """Create a new todo item"""
        todo_id = str(uuid.uuid4())
        todo = TodoItem(
            id=todo_id,
            title=todo_create.title,
            description=todo_create.description,
            priority=todo_create.priority,
            due_date=todo_create.due_date,
            tags=todo_create.tags
        )
        self._todos[todo_id] = todo
        return todo

    def get(self, todo_id: str) -> Optional[TodoItem]:
        """Get a todo item by ID"""
        return self._todos.get(todo_id)

    def list(self, status: Optional[TodoStatus] = None, tag: Optional[str] = None) -> List[TodoItem]:
        """List all todo items, optionally filtered by status or tag"""
        todos = list(self._todos.values())

        if status:
            todos = [t for t in todos if t.status == status]

        if tag:
            todos = [t for t in todos if tag in t.tags]

        # Sort by priority (high first) and creation date
        priority_order = {"high": 0, "medium": 1, "low": 2}
        todos.sort(key=lambda t: (priority_order[t.priority], t.created_at))

        return todos

    def update(self, todo_id: str, todo_update: TodoUpdate) -> Optional[TodoItem]:
        """Update a todo item"""
        todo = self._todos.get(todo_id)
        if not todo:
            return None

        update_data = todo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)

        todo.updated_at = datetime.utcnow()
        return todo

    def delete(self, todo_id: str) -> bool:
        """Delete a todo item"""
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False

    def get_stats(self) -> dict:
        """Get statistics about todos"""
        all_todos = list(self._todos.values())
        return {
            "total": len(all_todos),
            "pending": len([t for t in all_todos if t.status == TodoStatus.PENDING]),
            "in_progress": len([t for t in all_todos if t.status == TodoStatus.IN_PROGRESS]),
            "completed": len([t for t in all_todos if t.status == TodoStatus.COMPLETED]),
            "high_priority": len([t for t in all_todos if t.priority == "high"]),
        }


# Global storage instance
storage = TodoStorage()
