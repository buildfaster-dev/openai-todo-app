"""Tests for the storage module"""

import pytest
from src.todo_app.models import TodoCreate, TodoUpdate, TodoStatus, TodoPriority
from src.todo_app.storage import TodoStorage


@pytest.fixture
def storage():
    """Create a fresh storage instance for each test"""
    return TodoStorage()


def test_create_todo(storage):
    """Test creating a new todo"""
    # Clear sample data first
    storage._todos.clear()

    todo_create = TodoCreate(
        title="Test Todo",
        description="Test Description",
        priority=TodoPriority.HIGH
    )

    todo = storage.create(todo_create)

    assert todo.id is not None
    assert todo.title == "Test Todo"
    assert todo.description == "Test Description"
    assert todo.priority == TodoPriority.HIGH
    assert todo.status == TodoStatus.PENDING


def test_get_todo(storage):
    """Test retrieving a todo by ID"""
    storage._todos.clear()

    todo_create = TodoCreate(title="Test Todo")
    created_todo = storage.create(todo_create)

    retrieved_todo = storage.get(created_todo.id)

    assert retrieved_todo is not None
    assert retrieved_todo.id == created_todo.id
    assert retrieved_todo.title == "Test Todo"


def test_get_nonexistent_todo(storage):
    """Test retrieving a non-existent todo"""
    todo = storage.get("nonexistent-id")
    assert todo is None


def test_list_todos(storage):
    """Test listing all todos"""
    storage._todos.clear()

    storage.create(TodoCreate(title="Todo 1"))
    storage.create(TodoCreate(title="Todo 2"))
    storage.create(TodoCreate(title="Todo 3"))

    todos = storage.list()
    assert len(todos) == 3


def test_list_todos_by_status(storage):
    """Test filtering todos by status"""
    storage._todos.clear()

    todo1 = storage.create(TodoCreate(title="Todo 1"))
    todo2 = storage.create(TodoCreate(title="Todo 2"))

    # Update one to completed
    storage.update(todo1.id, TodoUpdate(status=TodoStatus.COMPLETED))

    pending_todos = storage.list(status=TodoStatus.PENDING)
    completed_todos = storage.list(status=TodoStatus.COMPLETED)

    assert len(pending_todos) == 1
    assert len(completed_todos) == 1


def test_list_todos_by_tag(storage):
    """Test filtering todos by tag"""
    storage._todos.clear()

    storage.create(TodoCreate(title="Todo 1", tags=["work"]))
    storage.create(TodoCreate(title="Todo 2", tags=["personal"]))
    storage.create(TodoCreate(title="Todo 3", tags=["work", "urgent"]))

    work_todos = storage.list(tag="work")
    assert len(work_todos) == 2


def test_update_todo(storage):
    """Test updating a todo"""
    storage._todos.clear()

    todo = storage.create(TodoCreate(title="Original Title"))

    updated_todo = storage.update(
        todo.id,
        TodoUpdate(
            title="Updated Title",
            status=TodoStatus.IN_PROGRESS
        )
    )

    assert updated_todo is not None
    assert updated_todo.title == "Updated Title"
    assert updated_todo.status == TodoStatus.IN_PROGRESS


def test_update_nonexistent_todo(storage):
    """Test updating a non-existent todo"""
    result = storage.update("nonexistent-id", TodoUpdate(title="New Title"))
    assert result is None


def test_delete_todo(storage):
    """Test deleting a todo"""
    storage._todos.clear()

    todo = storage.create(TodoCreate(title="To Delete"))

    result = storage.delete(todo.id)
    assert result is True

    # Verify it's gone
    retrieved = storage.get(todo.id)
    assert retrieved is None


def test_delete_nonexistent_todo(storage):
    """Test deleting a non-existent todo"""
    result = storage.delete("nonexistent-id")
    assert result is False


def test_get_stats(storage):
    """Test getting todo statistics"""
    storage._todos.clear()

    # Create todos with different statuses
    storage.create(TodoCreate(title="Todo 1", priority=TodoPriority.HIGH))
    todo2 = storage.create(TodoCreate(title="Todo 2"))
    todo3 = storage.create(TodoCreate(title="Todo 3"))

    storage.update(todo2.id, TodoUpdate(status=TodoStatus.IN_PROGRESS))
    storage.update(todo3.id, TodoUpdate(status=TodoStatus.COMPLETED))

    stats = storage.get_stats()

    assert stats["total"] == 3
    assert stats["pending"] == 1
    assert stats["in_progress"] == 1
    assert stats["completed"] == 1
    assert stats["high_priority"] == 1
