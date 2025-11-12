"""MCP Server for OpenAI ToDo App using official MCP Python SDK

This server follows the OpenAI Apps SDK pattern for serving UI widgets in ChatGPT.
It implements the MCP protocol with resources for HTML widgets and tools that
reference those widgets via openai/outputTemplate metadata.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .models import TodoCreate, TodoUpdate, TodoStatus
from .storage import storage


# MIME type for HTML widgets in OpenAI Apps SDK
MIME_TYPE = "text/html+skybridge"


@dataclass(frozen=True)
class TodoWidget:
    """Widget configuration for a todo tool"""
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    response_text: str


# Define available widgets
widgets: List[TodoWidget] = [
    TodoWidget(
        identifier="show_todo_app",
        title="Show Todo App",
        template_uri="ui://widget/todo-app.html",
        invoking="Loading your todos",
        invoked="Todos loaded",
        response_text="Here are your todos!",
    ),
    TodoWidget(
        identifier="show_todo_stats",
        title="Show Todo Statistics",
        template_uri="ui://widget/todo-stats.html",
        invoking="Calculating statistics",
        invoked="Statistics ready",
        response_text="Here are your todo statistics!",
    ),
]


WIDGETS_BY_ID: Dict[str, TodoWidget] = {
    widget.identifier: widget for widget in widgets
}
WIDGETS_BY_URI: Dict[str, TodoWidget] = {
    widget.template_uri: widget for widget in widgets
}


# Initialize MCP server with stateless HTTP mode
mcp = FastMCP(
    name="openai-todo-app",
    stateless_http=True,
)


# Input schemas for tools
class CreateTodoInput(BaseModel):
    """Schema for creating a todo"""
    title: str = Field(..., description="The title of the todo item")
    description: str = Field(default="", description="A detailed description of the todo")
    priority: str = Field(default="medium", description="Priority level: low, medium, or high")

    model_config = ConfigDict(extra="forbid")


class UpdateTodoInput(BaseModel):
    """Schema for updating a todo"""
    todo_id: str = Field(..., alias="todoId", description="The ID of the todo to update")
    status: Optional[str] = Field(None, description="New status: pending, in_progress, or completed")
    title: Optional[str] = Field(None, description="New title for the todo")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class DeleteTodoInput(BaseModel):
    """Schema for deleting a todo"""
    todo_id: str = Field(..., alias="todoId", description="The ID of the todo to delete")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class GetTodoInput(BaseModel):
    """Schema for getting a specific todo"""
    todo_id: str = Field(..., alias="todoId", description="The ID of the todo to retrieve")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


def _tool_meta(widget: TodoWidget) -> Dict[str, Any]:
    """Generate metadata for tools that support widgets"""
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }


def _tool_invocation_meta(widget: TodoWidget) -> Dict[str, Any]:
    """Generate metadata for tool invocation status messages"""
    return {
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
    }


def _get_todo_list_html() -> str:
    """Generate interactive HTML for todo list widget"""
    todos = storage.list()
    todos_data = [todo.model_dump() for todo in todos]
    stats = storage.get_stats()

    # Serialize todos data for JavaScript
    import json
    todos_json = json.dumps(todos_data)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo App</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 16px;
            background: white;
            max-width: 100%;
        }}
        .header {{
            font-size: 24px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }}

        /* Stats */
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .stat-label {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
        }}

        /* Add Todo Form */
        .add-todo-section {{
            background: #f9fafb;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .add-todo-title {{
            font-weight: 600;
            color: #374151;
            margin-bottom: 12px;
        }}
        .form-group {{
            margin-bottom: 12px;
        }}
        .form-label {{
            display: block;
            font-size: 13px;
            font-weight: 500;
            color: #374151;
            margin-bottom: 4px;
        }}
        .form-input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
        }}
        .form-input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        .form-select {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
            background: white;
        }}
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        .btn-primary:hover {{
            background: #5568d3;
        }}
        .btn-success {{
            background: #10b981;
            color: white;
            padding: 6px 12px;
            font-size: 12px;
        }}
        .btn-success:hover {{
            background: #059669;
        }}
        .btn-danger {{
            background: #ef4444;
            color: white;
            padding: 6px 12px;
            font-size: 12px;
        }}
        .btn-danger:hover {{
            background: #dc2626;
        }}
        .btn-secondary {{
            background: #6b7280;
            color: white;
            padding: 6px 12px;
            font-size: 12px;
        }}
        .btn-secondary:hover {{
            background: #4b5563;
        }}

        /* Filters */
        .filters {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 6px 12px;
            border: 1px solid #d1d5db;
            background: white;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .filter-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        .filter-btn:hover {{
            border-color: #667eea;
        }}

        /* Todo Items */
        .todos {{
            margin-top: 16px;
        }}
        .todo-item {{
            padding: 12px;
            margin: 8px 0;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid;
            position: relative;
        }}
        .todo-item.priority-high {{
            border-left-color: #dc2626;
        }}
        .todo-item.priority-medium {{
            border-left-color: #f59e0b;
        }}
        .todo-item.priority-low {{
            border-left-color: #3b82f6;
        }}
        .todo-item.status-completed .todo-title {{
            text-decoration: line-through;
            opacity: 0.6;
        }}
        .todo-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 8px;
        }}
        .todo-title {{
            font-weight: 600;
            color: #1f2937;
            flex: 1;
        }}
        .todo-description {{
            color: #6b7280;
            font-size: 13px;
            margin-bottom: 8px;
        }}
        .todo-meta {{
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 8px;
        }}
        .todo-actions {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .empty {{
            text-align: center;
            padding: 40px;
            color: #9ca3af;
        }}

        /* Edit Mode */
        .edit-form {{
            margin-top: 8px;
            padding: 12px;
            background: white;
            border-radius: 6px;
            border: 1px solid #d1d5db;
        }}
        .edit-actions {{
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }}

        /* Loading */
        .loading {{
            text-align: center;
            color: #6b7280;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">📝 Your Todo App</div>

    <div class="stats" id="stats">
        <div class="stat-card">
            <div class="stat-number" id="stat-total">{stats['total']}</div>
            <div class="stat-label">Total</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="stat-pending">{stats['pending']}</div>
            <div class="stat-label">Pending</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="stat-progress">{stats['in_progress']}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="stat-completed">{stats['completed']}</div>
            <div class="stat-label">Completed</div>
        </div>
    </div>

    <div class="add-todo-section">
        <div class="add-todo-title">➕ Add New Todo</div>
        <form id="addTodoForm" onsubmit="return false;">
            <div class="form-group">
                <label class="form-label">Title *</label>
                <input type="text" class="form-input" id="newTodoTitle" placeholder="Enter todo title..." required>
            </div>
            <div class="form-group">
                <label class="form-label">Description</label>
                <input type="text" class="form-input" id="newTodoDescription" placeholder="Enter description (optional)">
            </div>
            <div class="form-group">
                <label class="form-label">Priority</label>
                <select class="form-select" id="newTodoPriority">
                    <option value="low">🔵 Low</option>
                    <option value="medium" selected>🟡 Medium</option>
                    <option value="high">🔴 High</option>
                </select>
            </div>
            <button type="button" class="btn btn-primary" onclick="addTodo()">Add Todo</button>
        </form>
    </div>

    <div class="filters">
        <button class="filter-btn active" onclick="filterTodos('all')">All</button>
        <button class="filter-btn" onclick="filterTodos('pending')">Pending</button>
        <button class="filter-btn" onclick="filterTodos('in_progress')">In Progress</button>
        <button class="filter-btn" onclick="filterTodos('completed')">Completed</button>
    </div>

    <div class="todos" id="todoList"></div>

    <script>
        let todos = {todos_json};
        let currentFilter = 'all';
        let editingId = null;

        // Get API base URL (relative to current page)
        const API_BASE = window.location.origin + '/api';

        // Render todos
        function renderTodos() {{
            const filtered = currentFilter === 'all'
                ? todos
                : todos.filter(t => t.status === currentFilter);

            const container = document.getElementById('todoList');

            if (filtered.length === 0) {{
                container.innerHTML = '<div class="empty">No todos found. Create one above!</div>';
                return;
            }}

            container.innerHTML = filtered.map(todo => `
                <div class="todo-item priority-${{todo.priority}} status-${{todo.status}}" id="todo-${{todo.id}}">
                    <div class="todo-header">
                        <div class="todo-title">
                            ${{getStatusIcon(todo.status)}} ${{todo.title}}
                        </div>
                    </div>
                    ${{todo.description ? `<div class="todo-description">${{todo.description}}</div>` : ''}}
                    <div class="todo-meta">
                        Priority: ${{todo.priority.toUpperCase()}} • Status: ${{formatStatus(todo.status)}}
                    </div>
                    <div class="todo-actions">
                        ${{todo.status !== 'in_progress' ? `<button class="btn btn-secondary" onclick="updateStatus('${{todo.id}}', 'in_progress')">⏳ In Progress</button>` : ''}}
                        ${{todo.status !== 'completed' ? `<button class="btn btn-success" onclick="updateStatus('${{todo.id}}', 'completed')">✅ Complete</button>` : ''}}
                        ${{todo.status !== 'pending' ? `<button class="btn btn-secondary" onclick="updateStatus('${{todo.id}}', 'pending')">📝 Reopen</button>` : ''}}
                        <button class="btn btn-secondary" onclick="startEdit('${{todo.id}}')">✏️ Edit</button>
                        <button class="btn btn-danger" onclick="deleteTodo('${{todo.id}}')">🗑️ Delete</button>
                    </div>
                    <div id="edit-${{todo.id}}"></div>
                </div>
            `).join('');
        }}

        function getStatusIcon(status) {{
            if (status === 'completed') return '✅';
            if (status === 'in_progress') return '⏳';
            return '📝';
        }}

        function formatStatus(status) {{
            return status.replace('_', ' ').split(' ').map(w =>
                w.charAt(0).toUpperCase() + w.slice(1)
            ).join(' ');
        }}

        // Filter todos
        function filterTodos(filter) {{
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            renderTodos();
        }}

        // Add todo
        async function addTodo() {{
            const title = document.getElementById('newTodoTitle').value.trim();
            const description = document.getElementById('newTodoDescription').value.trim();
            const priority = document.getElementById('newTodoPriority').value;

            if (!title) {{
                alert('Please enter a title');
                return;
            }}

            try {{
                const response = await fetch(`${{API_BASE}}/todos`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ title, description, priority }})
                }});

                if (response.ok) {{
                    const newTodo = await response.json();
                    todos.push(newTodo);

                    // Clear form
                    document.getElementById('newTodoTitle').value = '';
                    document.getElementById('newTodoDescription').value = '';
                    document.getElementById('newTodoPriority').value = 'medium';

                    await loadStats();
                    renderTodos();
                }} else {{
                    alert('Error creating todo');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                alert('Error creating todo');
            }}
        }}

        // Update status
        async function updateStatus(id, status) {{
            try {{
                const response = await fetch(`${{API_BASE}}/todos/${{id}}`, {{
                    method: 'PATCH',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ status }})
                }});

                if (response.ok) {{
                    const updated = await response.json();
                    todos = todos.map(t => t.id === id ? updated : t);
                    await loadStats();
                    renderTodos();
                }} else {{
                    alert('Error updating todo');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                alert('Error updating todo');
            }}
        }}

        // Delete todo
        async function deleteTodo(id) {{
            if (!confirm('Are you sure you want to delete this todo?')) {{
                return;
            }}

            try {{
                const response = await fetch(`${{API_BASE}}/todos/${{id}}`, {{
                    method: 'DELETE'
                }});

                if (response.ok) {{
                    todos = todos.filter(t => t.id !== id);
                    await loadStats();
                    renderTodos();
                }} else {{
                    alert('Error deleting todo');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                alert('Error deleting todo');
            }}
        }}

        // Start edit
        function startEdit(id) {{
            const todo = todos.find(t => t.id === id);
            if (!todo) return;

            editingId = id;
            const editContainer = document.getElementById(`edit-${{id}}`);

            editContainer.innerHTML = `
                <div class="edit-form">
                    <div class="form-group">
                        <label class="form-label">Title</label>
                        <input type="text" class="form-input" id="edit-title-${{id}}" value="${{todo.title}}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Description</label>
                        <input type="text" class="form-input" id="edit-desc-${{id}}" value="${{todo.description || ''}}">
                    </div>
                    <div class="edit-actions">
                        <button class="btn btn-primary" onclick="saveEdit('${{id}}')">💾 Save</button>
                        <button class="btn btn-secondary" onclick="cancelEdit('${{id}}')">❌ Cancel</button>
                    </div>
                </div>
            `;
        }}

        // Save edit
        async function saveEdit(id) {{
            const title = document.getElementById(`edit-title-${{id}}`).value.trim();
            const description = document.getElementById(`edit-desc-${{id}}`).value.trim();

            if (!title) {{
                alert('Title cannot be empty');
                return;
            }}

            try {{
                const response = await fetch(`${{API_BASE}}/todos/${{id}}`, {{
                    method: 'PATCH',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ title, description }})
                }});

                if (response.ok) {{
                    const updated = await response.json();
                    todos = todos.map(t => t.id === id ? updated : t);
                    editingId = null;
                    renderTodos();
                }} else {{
                    alert('Error updating todo');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                alert('Error updating todo');
            }}
        }}

        // Cancel edit
        function cancelEdit(id) {{
            editingId = null;
            document.getElementById(`edit-${{id}}`).innerHTML = '';
        }}

        // Load stats
        async function loadStats() {{
            try {{
                const response = await fetch(`${{API_BASE}}/stats`);
                if (response.ok) {{
                    const stats = await response.json();
                    document.getElementById('stat-total').textContent = stats.total;
                    document.getElementById('stat-pending').textContent = stats.pending;
                    document.getElementById('stat-progress').textContent = stats.in_progress;
                    document.getElementById('stat-completed').textContent = stats.completed;
                }}
            }} catch (error) {{
                console.error('Error loading stats:', error);
            }}
        }}

        // Initial render
        renderTodos();

        // Enable Enter key for add todo
        document.getElementById('newTodoTitle').addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') addTodo();
        }});
    </script>
</body>
</html>"""


def _get_stats_html() -> str:
    """Generate interactive HTML for stats widget"""
    stats = storage.get_stats()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo Statistics</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: white;
        }}
        .header {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #111827;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .refresh-btn {{
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }}
        .refresh-btn:hover {{
            background: #5568d3;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
        }}
        .stat-number {{
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .progress-bar {{
            background: #f3f4f6;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 8px;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #10b981, #059669);
            height: 100%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 11px;
            font-weight: 600;
        }}
        .insights {{
            background: #f9fafb;
            padding: 16px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .insight-title {{
            font-weight: 600;
            margin-bottom: 12px;
            color: #374151;
        }}
        .insight-item {{
            padding: 8px 0;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <span>📊 Todo Statistics</span>
        <button class="refresh-btn" onclick="refreshStats()">🔄 Refresh</button>
    </div>

    <div class="stats-grid" id="statsGrid">
        <div class="stat-card">
            <div class="stat-number" id="stat-total">{stats['total']}</div>
            <div class="stat-label">Total Todos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="stat-pending">{stats['pending']}</div>
            <div class="stat-label">Pending</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="stat-progress">{stats['in_progress']}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="stat-completed">{stats['completed']}</div>
            <div class="stat-label">Completed</div>
        </div>
    </div>

    <div class="insights">
        <div class="insight-title">Completion Progress</div>
        <div class="progress-bar">
            <div class="progress-fill" id="progressBar" style="width: {stats['completed'] / max(stats['total'], 1) * 100:.0f}%">
                {stats['completed'] / max(stats['total'], 1) * 100:.0f}%
            </div>
        </div>

        <div class="insight-title">Insights</div>
        <div id="insights">
            <div class="insight-item">
                📝 {stats['pending']} task{'' if stats['pending'] == 1 else 's'} waiting to be started
            </div>
            <div class="insight-item">
                ⏳ {stats['in_progress']} task{'' if stats['in_progress'] == 1 else 's'} currently in progress
            </div>
            <div class="insight-item">
                ✅ {stats['completed']} task{'' if stats['completed'] == 1 else 's'} completed
            </div>
            {f'<div class="insight-item" style="color: #10b981; font-weight: 600;">🎉 All tasks completed!</div>' if stats['total'] > 0 and stats['completed'] == stats['total'] else ''}
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin + '/api';

        async function refreshStats() {{
            try {{
                const response = await fetch(`${{API_BASE}}/stats`);
                if (!response.ok) throw new Error('Failed to fetch stats');

                const stats = await response.json();

                // Update stat numbers
                document.getElementById('stat-total').textContent = stats.total;
                document.getElementById('stat-pending').textContent = stats.pending;
                document.getElementById('stat-progress').textContent = stats.in_progress;
                document.getElementById('stat-completed').textContent = stats.completed;

                // Update progress bar
                const percentage = stats.total > 0 ? (stats.completed / stats.total * 100).toFixed(0) : 0;
                const progressBar = document.getElementById('progressBar');
                progressBar.style.width = percentage + '%';
                progressBar.textContent = percentage + '%';

                // Update insights
                const insightsHtml = `
                    <div class="insight-item">
                        📝 ${{stats.pending}} task${{stats.pending === 1 ? '' : 's'}} waiting to be started
                    </div>
                    <div class="insight-item">
                        ⏳ ${{stats.in_progress}} task${{stats.in_progress === 1 ? '' : 's'}} currently in progress
                    </div>
                    <div class="insight-item">
                        ✅ ${{stats.completed}} task${{stats.completed === 1 ? '' : 's'}} completed
                    </div>
                    ${{stats.total > 0 && stats.completed === stats.total
                        ? '<div class="insight-item" style="color: #10b981; font-weight: 600;">🎉 All tasks completed!</div>'
                        : ''}}
                `;
                document.getElementById('insights').innerHTML = insightsHtml;

            }} catch (error) {{
                console.error('Error refreshing stats:', error);
                alert('Error refreshing statistics');
            }}
        }}
    </script>
</body>
</html>"""


# MCP Protocol Handlers

@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List all available tools"""
    tools = []

    # Widget-based tools
    for widget in widgets:
        if widget.identifier == "show_todo_app":
            tools.append(types.Tool(
                name=widget.identifier,
                title=widget.title,
                description="Open the full todo app interface showing all your todos and statistics",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
                _meta=_tool_meta(widget),
                annotations={
                    "destructiveHint": False,
                    "openWorldHint": False,
                    "readOnlyHint": True,
                },
            ))
        elif widget.identifier == "show_todo_stats":
            tools.append(types.Tool(
                name=widget.identifier,
                title=widget.title,
                description="Display todo statistics with a visual dashboard",
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
                _meta=_tool_meta(widget),
                annotations={
                    "destructiveHint": False,
                    "openWorldHint": False,
                    "readOnlyHint": True,
                },
            ))

    # Regular tools
    tools.extend([
        types.Tool(
            name="create_todo",
            title="Create Todo",
            description="Create a new todo item with title, description, and priority",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the todo item"},
                    "description": {"type": "string", "description": "A detailed description of the todo", "default": ""},
                    "priority": {"type": "string", "description": "Priority level: low, medium, or high", "default": "medium"},
                },
                "required": ["title"],
                "additionalProperties": False,
            },
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": False,
            },
        ),
        types.Tool(
            name="list_todos",
            title="List Todos",
            description="List all todo items with optional status filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status: pending, in_progress, or completed", "default": None},
                },
                "additionalProperties": False,
            },
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": True,
            },
        ),
        types.Tool(
            name="update_todo",
            title="Update Todo",
            description="Update an existing todo item's status or title",
            inputSchema={
                "type": "object",
                "properties": {
                    "todoId": {"type": "string", "description": "The ID of the todo to update"},
                    "status": {"type": "string", "description": "New status: pending, in_progress, or completed"},
                    "title": {"type": "string", "description": "New title for the todo"},
                },
                "required": ["todoId"],
                "additionalProperties": False,
            },
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": False,
            },
        ),
        types.Tool(
            name="delete_todo",
            title="Delete Todo",
            description="Delete a todo item by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "todoId": {"type": "string", "description": "The ID of the todo to delete"},
                },
                "required": ["todoId"],
                "additionalProperties": False,
            },
            annotations={
                "destructiveHint": True,
                "openWorldHint": False,
                "readOnlyHint": False,
            },
        ),
        types.Tool(
            name="get_todo",
            title="Get Todo",
            description="Get a specific todo item by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "todoId": {"type": "string", "description": "The ID of the todo to retrieve"},
                },
                "required": ["todoId"],
                "additionalProperties": False,
            },
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": True,
            },
        ),
    ])

    return tools


@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    """List all widget resources"""
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=f"{widget.title} widget markup",
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp._mcp_server.list_resource_templates()
async def _list_resource_templates() -> List[types.ResourceTemplate]:
    """List all resource templates"""
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=f"{widget.title} widget markup",
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    """Handle resource read requests for widget HTML"""
    widget = WIDGETS_BY_URI.get(str(req.params.uri))
    if widget is None:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )

    # Generate HTML based on widget type
    if widget.identifier == "show_todo_app":
        html = _get_todo_list_html()
    elif widget.identifier == "show_todo_stats":
        html = _get_stats_html()
    else:
        html = "<html><body>Widget not implemented</body></html>"

    contents = [
        types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=html,
            _meta=_tool_meta(widget),
        )
    ]

    return types.ServerResult(types.ReadResourceResult(contents=contents))


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool call requests"""
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    # Widget-based tools
    widget = WIDGETS_BY_ID.get(tool_name)
    if widget:
        todos = storage.list()
        stats = storage.get_stats()

        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=widget.response_text,
                    )
                ],
                structuredContent={
                    "todos": [todo.model_dump() for todo in todos],
                    "stats": stats,
                },
                _meta=_tool_invocation_meta(widget),
            )
        )

    # Regular tools
    try:
        if tool_name == "create_todo":
            payload = CreateTodoInput.model_validate(arguments)
            todo_create = TodoCreate(
                title=payload.title,
                description=payload.description if payload.description else None,
                priority=payload.priority
            )
            todo = storage.create(todo_create)
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Created todo: {todo.title}",
                        )
                    ],
                    structuredContent={"todo": todo.model_dump()},
                )
            )

        elif tool_name == "list_todos":
            status = arguments.get("status")
            todos = storage.list(status=TodoStatus(status) if status else None)
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Found {len(todos)} todos",
                        )
                    ],
                    structuredContent={
                        "todos": [todo.model_dump() for todo in todos],
                        "count": len(todos),
                    },
                )
            )

        elif tool_name == "update_todo":
            payload = UpdateTodoInput.model_validate(arguments)
            update_data = {}
            if payload.status:
                update_data["status"] = TodoStatus(payload.status)
            if payload.title:
                update_data["title"] = payload.title

            todo_update = TodoUpdate(**update_data)
            todo = storage.update(payload.todo_id, todo_update)

            if not todo:
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="Todo not found",
                            )
                        ],
                        isError=True,
                    )
                )

            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Updated todo: {todo.title}",
                        )
                    ],
                    structuredContent={"todo": todo.model_dump()},
                )
            )

        elif tool_name == "delete_todo":
            payload = DeleteTodoInput.model_validate(arguments)
            if storage.delete(payload.todo_id):
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="Todo deleted successfully",
                            )
                        ],
                        structuredContent={"success": True},
                    )
                )
            else:
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="Todo not found",
                            )
                        ],
                        isError=True,
                    )
                )

        elif tool_name == "get_todo":
            payload = GetTodoInput.model_validate(arguments)
            todo = storage.get(payload.todo_id)
            if not todo:
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="Todo not found",
                            )
                        ],
                        isError=True,
                    )
                )

            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Todo: {todo.title}",
                        )
                    ],
                    structuredContent={"todo": todo.model_dump()},
                )
            )

        else:
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Unknown tool: {tool_name}",
                        )
                    ],
                    isError=True,
                )
            )

    except ValidationError as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Input validation error: {exc.errors()}",
                    )
                ],
                isError=True,
            )
        )
    except Exception as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(exc)}",
                    )
                ],
                isError=True,
            )
        )


# Register custom handlers
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource
