# OpenAI Apps SDK Setup Guide

## Current Status

✅ **MCP Tools Working**: You confirmed the tools work (create_todo, list_todos, etc.)
❌ **UI Widgets Not Showing**: Need to configure UI component display
❌ **MCP Endpoint Issues**: Getting 400/SSE errors when OpenAI tries to refresh

## The Problem

The MCP endpoint at `/mcp/` is returning:
```json
{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept text/event-stream"}}
```

This suggests a transport configuration issue between FastMCP and OpenAI Apps SDK.

## Possible Solutions

### Option 1: Use the Full Web UI Instead of MCP

Instead of using MCP protocol for UI, direct OpenAI to your full web interface:

1. **In OpenAI Apps Platform**, set the UI URL to:
   ```
   https://YOUR-NGROK-URL.ngrok-free.dev/
   ```

2. This shows the full todo app interface (the one at localhost:8000)

### Option 2: Try SSE Transport

Since the error mentions SSE, maybe OpenAI expects SSE transport:

**Edit `src/todo_app/main.py`:**
```python
# Try SSE transport instead
mcp_http_app = mcp.http_app(path="/", transport="sse")
```

### Option 3: Use Official MCP Python SDK

Switch from FastMCP to the official MCP SDK:

**Install:**
```bash
uv add mcp
```

**Then implement using official SDK** (more complex, but might be more compatible)

### Option 4: Check OpenAI Apps SDK Requirements

The OpenAI Apps SDK might have specific requirements for:
- Endpoint paths
- Authentication headers
- CORS configuration
- Protocol version

## What's Working

Your MCP tools ARE working since you can:
- Create todos
- List todos
- Get statistics
- Update todos

The issue is just with:
1. UI component display
2. Endpoint refresh errors

## UI Components

The UI components in `ui_components.py` return this format:
```python
{
  "type": "component",
  "component": {
    "type": "html",
    "html": "<div>...</div>",
    "height": 400,
    "width": 600
  }
}
```

**This format might need adjustment** for OpenAI Apps SDK. Check their documentation for the exact UI component format they expect.

## Recommended Next Steps

1. **Check OpenAI Apps SDK Documentation**:
   - Look for UI component format specification
   - Check MCP endpoint requirements
   - Verify transport protocol expectations

2. **Try the Web UI Approach**:
   - Point OpenAI to `https://YOUR-NGROK-URL/` for the UI
   - Keep using MCP tools for functionality

3. **Test with OpenAI Examples**:
   - Look at official OpenAI Apps SDK Python examples
   - Compare their MCP server setup with ours

4. **Contact OpenAI Support**:
   - The 400 error with "text/event-stream" message might be a bug or misconfiguration
   - They can clarify what transport/format they expect

## Current Configuration

- **FastMCP Version**: 2.13.0.2
- **Transport**: http (default, should be Streamable HTTP)
- **MCP Endpoint**: `/mcp/`
- **Tools**: 7 tools defined and working
- **UI Components**: Defined but not displaying

## Server URLs

- **Local**: http://localhost:8000
- **Ngrok**: https://YOUR-NGROK-URL.ngrok-free.dev
- **MCP Endpoint**: https://YOUR-NGROK-URL.ngrok-free.dev/mcp/
- **Web UI**: https://YOUR-NGROK-URL.ngrok-free.dev/
- **API Health**: https://YOUR-NGROK-URL.ngrok-free.dev/api/health
