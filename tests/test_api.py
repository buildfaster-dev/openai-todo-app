"""Tests for the API endpoints"""

import pytest
from fastapi.testclient import TestClient
from src.todo_app.main import app
from src.todo_app.storage import storage


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset storage before each test"""
    storage._todos.clear()
    storage._initialize_sample_data()


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "openai-todo-app"


def test_create_todo(client):
    """Test creating a new todo via API"""
    response = client.post(
        "/api/todos",
        json={"title": "Test Todo", "priority": "high"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["priority"] == "high"
    assert "id" in data


def test_list_todos(client):
    """Test listing todos via API"""
    response = client.get("/api/todos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_todo(client):
    """Test getting a specific todo via API"""
    # First create a todo
    create_response = client.post(
        "/api/todos",
        json={"title": "Test Todo"}
    )
    todo_id = create_response.json()["id"]

    # Now get it
    response = client.get(f"/api/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id


def test_get_nonexistent_todo(client):
    """Test getting a non-existent todo"""
    response = client.get("/api/todos/nonexistent-id")
    assert response.status_code == 404


def test_update_todo(client):
    """Test updating a todo via API"""
    # Create a todo first
    create_response = client.post(
        "/api/todos",
        json={"title": "Original Title"}
    )
    todo_id = create_response.json()["id"]

    # Update it
    response = client.patch(
        f"/api/todos/{todo_id}",
        json={"title": "Updated Title", "status": "completed"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "completed"


def test_delete_todo(client):
    """Test deleting a todo via API"""
    # Create a todo first
    create_response = client.post(
        "/api/todos",
        json={"title": "To Delete"}
    )
    todo_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 200

    # Verify it's gone
    get_response = client.get(f"/api/todos/{todo_id}")
    assert get_response.status_code == 404


def test_get_stats(client):
    """Test getting statistics via API"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "pending" in data
    assert "in_progress" in data
    assert "completed" in data


def test_mcp_create_todo(client):
    """Test MCP create todo endpoint"""
    response = client.post(
        "/mcp/tools/create_todo",
        params={"title": "MCP Todo", "description": "Created via MCP"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["todo"]["title"] == "MCP Todo"


def test_mcp_list_todos(client):
    """Test MCP list todos endpoint"""
    response = client.get("/mcp/tools/list_todos")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "todos" in data
    assert "count" in data


def test_mcp_get_stats(client):
    """Test MCP get stats endpoint"""
    response = client.get("/mcp/tools/get_stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "stats" in data
