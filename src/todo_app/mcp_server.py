"""MCP Server for OpenAI ToDo App using FastMCP"""

from fastmcp import FastMCP
from typing import Optional
from .models import TodoCreate, TodoUpdate, TodoStatus
from .storage import storage
from .ui_components import create_todo_list_component, create_stats_component

# Initialize FastMCP server
mcp = FastMCP("OpenAI ToDo App")


@mcp.tool()
def create_todo(
    title: str,
    description: str = "",
    priority: str = "medium"
) -> dict:
    """
    Create a new todo item.

    Args:
        title: The title of the todo item
        description: A detailed description of the todo
        priority: Priority level - low, medium, or high

    Returns:
        Dictionary with success status and created todo
    """
    try:
        todo_create = TodoCreate(
            title=title,
            description=description if description else None,
            priority=priority
        )
        todo = storage.create(todo_create)
        return {
            "success": True,
            "todo": todo.model_dump(),
            "message": f"Todo '{title}' created successfully!"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_todos(status: Optional[str] = None, show_ui: bool = True) -> dict:
    """
    List all todo items with optional status filter and display them in a UI widget.

    Args:
        status: Optional filter by status - pending, in_progress, or completed
        show_ui: Whether to show a visual UI component (default: True)

    Returns:
        Dictionary with success status, list of todos, and optional UI component
    """
    try:
        todos = storage.list(status=TodoStatus(status) if status else None)
        todos_data = [todo.model_dump() for todo in todos]

        result = {
            "success": True,
            "todos": todos_data,
            "count": len(todos)
        }

        # Add UI component if requested
        if show_ui:
            filter_text = f" ({status.replace('_', ' ').title()})" if status else ""
            result["ui"] = create_todo_list_component(
                todos_data,
                title=f"Your Todos{filter_text}"
            )

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def update_todo(
    todo_id: str,
    status: Optional[str] = None,
    title: Optional[str] = None
) -> dict:
    """
    Update an existing todo item.

    Args:
        todo_id: The ID of the todo to update
        status: New status - pending, in_progress, or completed
        title: New title for the todo

    Returns:
        Dictionary with success status and updated todo
    """
    try:
        update_data = {}
        if status:
            update_data["status"] = TodoStatus(status)
        if title:
            update_data["title"] = title

        todo_update = TodoUpdate(**update_data)
        todo = storage.update(todo_id, todo_update)

        if not todo:
            return {"success": False, "error": "Todo not found"}

        return {
            "success": True,
            "todo": todo.model_dump(),
            "message": "Todo updated successfully!"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_stats(show_ui: bool = True) -> dict:
    """
    Get statistics about all todos with a visual dashboard.

    Args:
        show_ui: Whether to show a visual UI component (default: True)

    Returns:
        Dictionary with success status, statistics, and optional UI component
    """
    try:
        stats = storage.get_stats()
        result = {
            "success": True,
            "stats": stats
        }

        # Add UI component if requested
        if show_ui:
            result["ui"] = create_stats_component(stats)

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_todo(todo_id: str) -> dict:
    """
    Delete a todo item.

    Args:
        todo_id: The ID of the todo to delete

    Returns:
        Dictionary with success status
    """
    try:
        if storage.delete(todo_id):
            return {
                "success": True,
                "message": "Todo deleted successfully!"
            }
        else:
            return {"success": False, "error": "Todo not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_todo(todo_id: str) -> dict:
    """
    Get a specific todo item by ID.

    Args:
        todo_id: The ID of the todo to retrieve

    Returns:
        Dictionary with success status and todo data
    """
    try:
        todo = storage.get(todo_id)
        if not todo:
            return {"success": False, "error": "Todo not found"}

        return {
            "success": True,
            "todo": todo.model_dump()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def show_todo_app() -> dict:
    """
    Open the full todo app interface showing all your todos and statistics.

    This displays a comprehensive UI widget with your complete todo list
    and statistics dashboard.

    Returns:
        Dictionary with UI component displaying the full app
    """
    try:
        # Get all todos and stats
        todos = storage.list()
        stats = storage.get_stats()
        todos_data = [todo.model_dump() for todo in todos]

        return {
            "success": True,
            "message": "Opening Todo App...",
            "ui": create_todo_list_component(todos_data, title="📝 Your Todo App"),
            "stats_ui": create_stats_component(stats),
            "stats": stats,
            "todo_count": len(todos_data)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
