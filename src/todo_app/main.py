"""Main MCP server application for OpenAI Apps SDK

This serves the MCP server directly following the OpenAI Apps SDK pattern.
The server exposes tools with UI widgets for ChatGPT integration.
Also includes REST API endpoints for interactive widget functionality.
"""

import logging
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request
from .mcp_server import mcp
from .models import TodoCreate, TodoUpdate, TodoStatus
from .storage import storage

# Configurar logging para reducir ruido en desarrollo
# Suprime los tracebacks de MCP cuando se rechazan requests inválidos (como GET desde navegador)
logging.getLogger("mcp.server.streamable_http").setLevel(logging.ERROR)
logging.getLogger("anyio").setLevel(logging.ERROR)

# REST API endpoints for interactive UI
async def get_todos(request: Request) -> JSONResponse:
    """Get all todos with optional filters"""
    status_filter = request.query_params.get("status")
    tag_filter = request.query_params.get("tag")

    status_enum = TodoStatus(status_filter) if status_filter else None
    todos = storage.list(status=status_enum, tag=tag_filter)

    return JSONResponse([todo.model_dump(mode='json') for todo in todos])


async def create_todo_endpoint(request: Request) -> JSONResponse:
    """Create a new todo"""
    data = await request.json()
    todo_create = TodoCreate(**data)
    todo = storage.create(todo_create)
    return JSONResponse(todo.model_dump(mode='json'), status_code=201)


async def get_todo(request: Request) -> JSONResponse:
    """Get a specific todo"""
    todo_id = request.path_params["todo_id"]
    todo = storage.get(todo_id)
    if not todo:
        return JSONResponse({"error": "Todo not found"}, status_code=404)
    return JSONResponse(todo.model_dump(mode='json'))


async def update_todo_endpoint(request: Request) -> JSONResponse:
    """Update a todo"""
    todo_id = request.path_params["todo_id"]
    data = await request.json()

    # Convert status string to enum if present
    if "status" in data and data["status"]:
        data["status"] = TodoStatus(data["status"])

    todo_update = TodoUpdate(**data)
    todo = storage.update(todo_id, todo_update)

    if not todo:
        return JSONResponse({"error": "Todo not found"}, status_code=404)
    return JSONResponse(todo.model_dump(mode='json'))


async def delete_todo_endpoint(request: Request) -> JSONResponse:
    """Delete a todo"""
    todo_id = request.path_params["todo_id"]
    if not storage.delete(todo_id):
        return JSONResponse({"error": "Todo not found"}, status_code=404)
    return JSONResponse({"message": "Todo deleted successfully"})


async def get_stats(request: Request) -> JSONResponse:
    """Get todo statistics"""
    return JSONResponse(storage.get_stats())


# Get MCP app and add REST API routes
app = mcp.streamable_http_app()

# Add REST API routes to the MCP app
app.routes.extend([
    Route("/api/todos", get_todos, methods=["GET"]),
    Route("/api/todos", create_todo_endpoint, methods=["POST"]),
    Route("/api/todos/{todo_id}", get_todo, methods=["GET"]),
    Route("/api/todos/{todo_id}", update_todo_endpoint, methods=["PATCH"]),
    Route("/api/todos/{todo_id}", delete_todo_endpoint, methods=["DELETE"]),
    Route("/api/stats", get_stats, methods=["GET"]),
])

# Add CORS middleware for OpenAI Apps SDK and widget interactivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: This server implements the MCP protocol with Streamable HTTP transport at /mcp
# Tools are defined in mcp_server.py with openai/outputTemplate metadata
# Widget HTML is served via MCP resources (ui://widget/*.html URIs)
# REST API endpoints (/api/*) enable interactive widget functionality


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
