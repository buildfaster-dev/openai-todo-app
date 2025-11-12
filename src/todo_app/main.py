"""Main FastAPI application with MCP server for ToDo app"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from pathlib import Path

from .models import TodoItem, TodoCreate, TodoUpdate, TodoStatus
from .storage import storage
from .mcp_server import mcp

# Create MCP HTTP app with default 'http' transport
# In FastMCP 2.x, 'http' is the modern Streamable HTTP protocol
# Set path="/" so routes are at root of the mounted app
mcp_http_app = mcp.http_app(path="/")

# Create main FastAPI app with MCP lifespan for proper task group initialization
app = FastAPI(
    title="OpenAI ToDo App",
    description="A ToDo application built with OpenAI Apps SDK and MCP",
    version="0.1.0",
    lifespan=mcp_http_app.lifespan,
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Mount MCP server at /mcp - endpoints will be accessible at /mcp/
app.mount("/mcp", mcp_http_app)


# UI and API Endpoints
@app.get("/")
async def root():
    """Root endpoint - serve the UI"""
    return HTMLResponse(content=get_html_content())


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "openai-todo-app"}


# Todo CRUD Endpoints
@app.post("/api/todos", response_model=TodoItem)
async def create_todo(todo: TodoCreate):
    """Create a new todo item"""
    return storage.create(todo)


@app.get("/api/todos", response_model=List[TodoItem])
async def list_todos(
    status: Optional[TodoStatus] = Query(None, description="Filter by status"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """List all todo items with optional filters"""
    return storage.list(status=status, tag=tag)


@app.get("/api/todos/{todo_id}", response_model=TodoItem)
async def get_todo(todo_id: str):
    """Get a specific todo item"""
    todo = storage.get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.patch("/api/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: str, todo_update: TodoUpdate):
    """Update a todo item"""
    todo = storage.update(todo_id, todo_update)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.delete("/api/todos/{todo_id}")
async def delete_todo(todo_id: str):
    """Delete a todo item"""
    if not storage.delete(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}


@app.get("/api/stats")
async def get_stats():
    """Get todo statistics"""
    return storage.get_stats()


# Note: MCP endpoints (/mcp/*) are handled by FastMCP with Streamable HTTP transport
# Streamable HTTP is the modern MCP protocol (replaced SSE as of spec 2025-03-26)
# The MCP server provides tool discovery and execution for OpenAI Apps SDK


def get_html_content() -> str:
    """Get the HTML content for the UI"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenAI ToDo App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
        }

        .stats {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }

        .stat {
            text-align: center;
        }

        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }

        .add-todo {
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }

        .input-group {
            display: flex;
            gap: 10px;
        }

        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .todos {
            padding: 20px;
        }

        .filter-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .tab {
            padding: 8px 16px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
        }

        .tab.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .todo-item {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            transition: all 0.3s;
        }

        .todo-item:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .todo-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .todo-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #2d3748;
        }

        .todo-priority {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }

        .priority-high {
            background: #fee;
            color: #c53030;
        }

        .priority-medium {
            background: #fef3c7;
            color: #92400e;
        }

        .priority-low {
            background: #e0f2fe;
            color: #075985;
        }

        .todo-description {
            color: #718096;
            margin-bottom: 10px;
        }

        .todo-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .todo-tags {
            display: flex;
            gap: 5px;
        }

        .tag {
            padding: 4px 8px;
            background: #f7fafc;
            border-radius: 6px;
            font-size: 0.8em;
            color: #4a5568;
        }

        .todo-actions {
            display: flex;
            gap: 10px;
        }

        .btn-small {
            padding: 6px 12px;
            font-size: 0.9em;
        }

        .btn-success {
            background: #48bb78;
            color: white;
        }

        .btn-danger {
            background: #f56565;
            color: white;
        }

        .status-completed .todo-title {
            text-decoration: line-through;
            opacity: 0.6;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #a0aec0;
        }

        .empty-state-icon {
            font-size: 4em;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ OpenAI ToDo App</h1>
            <p>Built with OpenAI Apps SDK & MCP</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number" id="stat-total">0</div>
                <div class="stat-label">Total</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="stat-pending">0</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="stat-progress">0</div>
                <div class="stat-label">In Progress</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="stat-completed">0</div>
                <div class="stat-label">Completed</div>
            </div>
        </div>

        <div class="add-todo">
            <div class="input-group">
                <input type="text" id="todo-input" placeholder="What needs to be done?" />
                <button class="btn btn-primary" onclick="addTodo()">Add Todo</button>
            </div>
        </div>

        <div class="todos">
            <div class="filter-tabs">
                <button class="tab active" onclick="filterTodos('all')">All</button>
                <button class="tab" onclick="filterTodos('pending')">Pending</button>
                <button class="tab" onclick="filterTodos('in_progress')">In Progress</button>
                <button class="tab" onclick="filterTodos('completed')">Completed</button>
            </div>
            <div id="todo-list"></div>
        </div>
    </div>

    <script>
        let currentFilter = 'all';

        async function loadTodos() {
            try {
                const response = await fetch('/api/todos');
                const todos = await response.json();
                renderTodos(todos);
                await loadStats();
            } catch (error) {
                console.error('Error loading todos:', error);
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('stat-total').textContent = stats.total;
                document.getElementById('stat-pending').textContent = stats.pending;
                document.getElementById('stat-progress').textContent = stats.in_progress;
                document.getElementById('stat-completed').textContent = stats.completed;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        function renderTodos(todos) {
            const todoList = document.getElementById('todo-list');

            const filteredTodos = currentFilter === 'all'
                ? todos
                : todos.filter(todo => todo.status === currentFilter);

            if (filteredTodos.length === 0) {
                todoList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📝</div>
                        <p>No todos found. Add one above!</p>
                    </div>
                `;
                return;
            }

            todoList.innerHTML = filteredTodos.map(todo => `
                <div class="todo-item status-${todo.status}">
                    <div class="todo-header">
                        <div class="todo-title">${todo.title}</div>
                        <div class="todo-priority priority-${todo.priority}">
                            ${todo.priority.toUpperCase()}
                        </div>
                    </div>
                    ${todo.description ? `<div class="todo-description">${todo.description}</div>` : ''}
                    <div class="todo-footer">
                        <div class="todo-tags">
                            ${todo.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        <div class="todo-actions">
                            ${todo.status !== 'completed' ?
                                `<button class="btn btn-small btn-success" onclick="completeTodo('${todo.id}')">✓ Complete</button>` :
                                ''}
                            <button class="btn btn-small btn-danger" onclick="deleteTodo('${todo.id}')">Delete</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        async function addTodo() {
            const input = document.getElementById('todo-input');
            const title = input.value.trim();

            if (!title) return;

            try {
                const response = await fetch('/api/todos', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ title }),
                });

                if (response.ok) {
                    input.value = '';
                    await loadTodos();
                }
            } catch (error) {
                console.error('Error adding todo:', error);
            }
        }

        async function completeTodo(id) {
            try {
                const response = await fetch(`/api/todos/${id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ status: 'completed' }),
                });

                if (response.ok) {
                    await loadTodos();
                }
            } catch (error) {
                console.error('Error completing todo:', error);
            }
        }

        async function deleteTodo(id) {
            if (!confirm('Are you sure you want to delete this todo?')) return;

            try {
                const response = await fetch(`/api/todos/${id}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    await loadTodos();
                }
            } catch (error) {
                console.error('Error deleting todo:', error);
            }
        }

        function filterTodos(filter) {
            currentFilter = filter;
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            loadTodos();
        }

        // Allow Enter key to add todo
        document.getElementById('todo-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                addTodo();
            }
        });

        // Load todos on page load
        loadTodos();
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
