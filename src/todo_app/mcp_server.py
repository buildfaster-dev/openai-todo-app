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
    """Generate HTML for todo list widget"""
    todos = storage.list()
    todos_data = [todo.model_dump() for todo in todos]
    stats = storage.get_stats()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo App</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 16px;
            background: white;
        }}
        .header {{
            font-size: 24px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }}
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
        .todo-item {{
            padding: 12px;
            margin: 8px 0;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid;
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
        .todo-title {{
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 4px;
        }}
        .todo-meta {{
            font-size: 12px;
            color: #9ca3af;
        }}
        .empty {{
            text-align: center;
            padding: 40px;
            color: #9ca3af;
        }}
    </style>
</head>
<body>
    <div class="header">📝 Your Todo App</div>
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{stats['total']}</div>
            <div class="stat-label">Total</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['pending']}</div>
            <div class="stat-label">Pending</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['in_progress']}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['completed']}</div>
            <div class="stat-label">Completed</div>
        </div>
    </div>
    <div class="todos">
        {''.join([f'''
        <div class="todo-item priority-{todo["priority"]}">
            <div class="todo-title">
                {todo["status"] == "completed" and "✅" or (todo["status"] == "in_progress" and "⏳" or "📝")}
                {todo["title"]}
            </div>
            {f'<div style="color: #6b7280; margin: 4px 0;">{todo["description"]}</div>' if todo.get("description") else ""}
            <div class="todo-meta">
                Priority: {todo["priority"].upper()} • Status: {todo["status"].replace("_", " ").title()}
            </div>
        </div>
        ''' for todo in todos_data]) if todos_data else '<div class="empty">No todos yet! Create one to get started.</div>'}
    </div>
</body>
</html>"""


def _get_stats_html() -> str:
    """Generate HTML for stats widget"""
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
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
            border-radius: 12px;
            text-align: center;
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
    </style>
</head>
<body>
    <div class="header">📊 Todo Statistics</div>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{stats['total']}</div>
            <div class="stat-label">Total Todos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['pending']}</div>
            <div class="stat-label">Pending</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['in_progress']}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['completed']}</div>
            <div class="stat-label">Completed</div>
        </div>
    </div>
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
