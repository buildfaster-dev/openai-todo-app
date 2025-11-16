# Tutorial: Build Your First MCP Application - Part 2

> **This is a continuation of the Notes App Tutorial**
> **If you haven't completed Part 1, please start there first**

## Part 3 (Continued): Building the MCP Server

### 3.6 Create the MCP Server - Step by Step

The MCP server is the heart of your application. It defines what ChatGPT can do. We'll build `src/notes_app/mcp_server.py` gradually.

**Step 1: Basic Setup and Imports**

Create `src/notes_app/mcp_server.py` with basic imports:

```python
"""MCP Server implementation for Notes App

This module defines the MCP tools and resources that ChatGPT can interact with.
"""

import os
from typing import Any, Dict, List

import mcp.types as types  # MCP protocol types
from dotenv import load_dotenv  # Load environment variables
from mcp.server.fastmcp import FastMCP  # MCP server framework
from pydantic import BaseModel, Field  # Data validation

from .models import NoteCreate, NoteUpdate  # Our data models
from .storage import storage  # Storage singleton

# Load environment variables from .env file
load_dotenv()

# Get public URL for widgets (from ngrok or deployment)
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")
```

**What this does:**
- Imports MCP types for protocol communication
- Imports FastMCP framework to simplify server creation
- Loads environment variables (like PUBLIC_URL for production)
- Imports our models and storage

**Step 2: Initialize MCP Server**

```python
# Initialize MCP server
mcp = FastMCP(
    name="notes-app",  # Server name (shown in ChatGPT)
    stateless_http=True,  # Use HTTP transport (not stdio or SSE)
)

# Widget configuration
WIDGETS_URI = "ui://widget/notes-list.html"  # URI for notes list widget
STATS_WIDGET_URI = "ui://widget/notes-stats.html"  # URI for stats widget
MIME_TYPE = "text/html+skybridge"  # Required MIME type for widgets
```

**What this does:**
- Creates a FastMCP server instance
- `stateless_http=True`: Uses HTTP (required for OpenAI Apps SDK)
- Defines widget URIs (special URI scheme for widgets)
- Sets MIME type for HTML widgets

**Step 3: Define Input Schemas**

Create Pydantic models for tool inputs:

```python
# ============================================================================
# MCP Tool Input Schemas (using Pydantic for validation)
# ============================================================================

class CreateNoteInput(BaseModel):
    """Input schema for creating a note

    This model validates the arguments passed when ChatGPT calls create_note.
    """
    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The content of the note")


class UpdateNoteInput(BaseModel):
    """Input schema for updating a note"""
    note_id: str = Field(..., alias="noteId", description="The ID of the note to update")
    title: str | None = Field(None, description="New title (optional)")
    content: str | None = Field(None, description="New content (optional)")


class DeleteNoteInput(BaseModel):
    """Input schema for deleting a note"""
    note_id: str = Field(..., alias="noteId", description="The ID of the note to delete")


class GetNoteInput(BaseModel):
    """Input schema for getting a specific note"""
    note_id: str = Field(..., alias="noteId", description="The ID of the note to retrieve")
```

**What this does:**
- Defines input validation for each tool
- `alias="noteId"`: Allows camelCase in JSON (converts to snake_case in Python)
- `Field(...)`: Required field
- `Field(None)`: Optional field

**Step 4: Create Simple Tool Definitions**

Let's start with the tool list handler:

```python
# ============================================================================
# MCP Protocol Handlers
# ============================================================================

@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List all available MCP tools

    This is called by ChatGPT to discover what tools are available.
    ChatGPT will only show tools that are defined here.
    """
    return [
        # CREATE NOTE TOOL
        types.Tool(
            name="create_note",  # Unique identifier (snake_case)
            title="Create Note",  # Display name
            description="Create a new note with a title and content",
            inputSchema={  # JSON Schema for validation
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the note"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content of the note"
                    },
                },
                "required": ["title", "content"],
                "additionalProperties": False,  # Don't allow extra fields
            },
            _meta={
                "openai/widgetAccessible": True,  # Tool can be called from widgets
            },
        ),
        # We'll add more tools here...
    ]
```

**What each field does:**
- `name`: Tool identifier (used in tool calls)
- `title`: Human-readable name
- `description`: Helps ChatGPT understand when to use the tool
- `inputSchema`: JSON Schema defining required arguments
- `additionalProperties: False`: Strict validation
- `_meta`: OpenAI-specific metadata

**Step 5: Add Remaining Tools**

Add the other tools to the list:

```python
        # LIST NOTES TOOL
        types.Tool(
            name="list_notes",
            title="List Notes",
            description="List all notes with an interactive widget",
            inputSchema={
                "type": "object",
                "properties": {},  # No arguments needed
                "additionalProperties": False,
            },
            _meta={
                "openai/outputTemplate": WIDGETS_URI,  # Show widget after calling
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True,  # This tool produces a widget
            },
        ),

        # GET NOTE TOOL
        types.Tool(
            name="get_note",
            title="Get Note",
            description="Get a specific note by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "noteId": {
                        "type": "string",
                        "description": "The ID of the note to retrieve"
                    },
                },
                "required": ["noteId"],
                "additionalProperties": False,
            },
        ),

        # UPDATE NOTE TOOL
        types.Tool(
            name="update_note",
            title="Update Note",
            description="Update an existing note's title or content",
            inputSchema={
                "type": "object",
                "properties": {
                    "noteId": {
                        "type": "string",
                        "description": "The ID of the note to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title (optional)"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content (optional)"
                    },
                },
                "required": ["noteId"],
                "additionalProperties": False,
            },
        ),

        # DELETE NOTE TOOL
        types.Tool(
            name="delete_note",
            title="Delete Note",
            description="Delete a note by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "noteId": {
                        "type": "string",
                        "description": "The ID of the note to delete"
                    },
                },
                "required": ["noteId"],
                "additionalProperties": False,
            },
            _meta={
                "openai/widgetAccessible": True,  # Can be called from widgets
            },
        ),

        # GET STATISTICS TOOL
        types.Tool(
            name="get_stats",
            title="Get Statistics",
            description="Get statistics about your notes",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            _meta={
                "openai/outputTemplate": STATS_WIDGET_URI,  # Show stats widget
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True,
            },
        ),
```

**Step 6: Create Tool Handlers**

Now implement the handlers that process tool calls:

```python
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool call requests from ChatGPT

    This function is called when ChatGPT executes a tool.
    It routes the request to the appropriate handler based on tool name.
    """
    tool_name = req.params.name  # Which tool is being called
    arguments = req.params.arguments or {}  # Tool arguments (as dict)

    # ===== CREATE NOTE =====
    if tool_name == "create_note":
        # Validate input using Pydantic
        payload = CreateNoteInput.model_validate(arguments)

        # Create the note
        note_create = NoteCreate(title=payload.title, content=payload.content)
        note = storage.create(note_create)

        # Return result to ChatGPT
        return types.ServerResult(
            types.CallToolResult(
                # Text content (shown in chat)
                content=[
                    types.TextContent(
                        type="text",
                        text=f"✅ Created note: **{note.title}**",
                    )
                ],
                # Structured content (passed to widgets)
                structuredContent={
                    "note": note.model_dump(mode='json')
                },
            )
        )

    # ===== LIST NOTES =====
    elif tool_name == "list_notes":
        notes = storage.list()
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"📝 You have {len(notes)} note(s)",
                    )
                ],
                structuredContent={
                    "notes": [note.model_dump(mode='json') for note in notes],
                    "count": len(notes),
                },
            )
        )

    # ===== GET NOTE =====
    elif tool_name == "get_note":
        payload = GetNoteInput.model_validate(arguments)
        note = storage.get(payload.note_id)

        if not note:
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text="❌ Note not found",
                        )
                    ],
                    isError=True,  # Mark as error
                )
            )

        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"**{note.title}**\n\n{note.content}",
                    )
                ],
                structuredContent={
                    "note": note.model_dump(mode='json')
                },
            )
        )

    # ===== UPDATE NOTE =====
    elif tool_name == "update_note":
        payload = UpdateNoteInput.model_validate(arguments)
        note_update = NoteUpdate(title=payload.title, content=payload.content)
        note = storage.update(payload.note_id, note_update)

        if not note:
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text="❌ Note not found",
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
                        text=f"✅ Updated note: **{note.title}**",
                    )
                ],
                structuredContent={
                    "note": note.model_dump(mode='json')
                },
            )
        )

    # ===== DELETE NOTE =====
    elif tool_name == "delete_note":
        payload = DeleteNoteInput.model_validate(arguments)
        success = storage.delete(payload.note_id)

        if success:
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text="✅ Note deleted successfully",
                        )
                    ],
                )
            )
        else:
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text="❌ Note not found",
                        )
                    ],
                    isError=True,
                )
            )

    # ===== GET STATISTICS =====
    elif tool_name == "get_stats":
        stats = storage.get_stats()
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"📊 Statistics: {stats.total} total notes, {stats.created_today} created today",
                    )
                ],
                structuredContent={
                    "stats": stats.model_dump(mode='json')
                },
            )
        )

    # ===== UNKNOWN TOOL =====
    else:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"❌ Unknown tool: {tool_name}",
                    )
                ],
                isError=True,
            )
        )


# Register the tool call handler
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
```

**What this does:**
- Routes tool calls based on `tool_name`
- Validates input with Pydantic models
- Calls storage methods to perform operations
- Returns results with both text content and structured content
- Handles errors gracefully with `isError=True`

🎓 **You learned**:
- How to define MCP tools with JSON schemas
- How to handle tool calls and route to appropriate handlers
- How to return both text and structured content
- How to handle errors in tool execution

### 3.7 Create main.py - Step by Step

The main file ties everything together. Create `src/notes_app/main.py`:

**Step 1: Basic Imports**

```python
"""Main application entry point

This file creates the FastAPI/Starlette application and configures middleware.
"""

from starlette.middleware.cors import CORSMiddleware
from .mcp_server import mcp
```

**What this does:**
- Imports CORS middleware for cross-origin requests
- Imports our MCP server

**Step 2: Create Application**

```python
# Get the Starlette app from FastMCP
# FastMCP creates a Starlette app automatically
app = mcp.streamable_http_app()
```

**What this does:**
- `streamable_http_app()`: Creates a Starlette app with MCP endpoints
- The app automatically handles `/mcp` endpoint

**Step 3: Add CORS Middleware**

```python
# Add CORS middleware for OpenAI Apps SDK
# This allows ChatGPT to make requests to our server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to OpenAI domains
    allow_credentials=False,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
```

**What this does:**
- Enables Cross-Origin Resource Sharing (CORS)
- `allow_origins=["*"]`: Allows requests from any origin (development only!)
- In production, restrict to ChatGPT domains

**Step 4: Add Development Runner**

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.notes_app.main:app",  # Module path to app
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,  # Port number
        reload=True  # Auto-reload on code changes
    )
```

**What this does:**
- Allows running the app directly with `python -m src.notes_app.main`
- Uvicorn is the ASGI server
- `reload=True`: Automatically restarts on code changes (development only)

**Complete main.py:**

```python
"""Main application entry point

This file creates the FastAPI/Starlette application and configures middleware.
"""

from starlette.middleware.cors import CORSMiddleware
from .mcp_server import mcp

# Get the Starlette app from FastMCP
app = mcp.streamable_http_app()

# Add CORS middleware for OpenAI Apps SDK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to OpenAI domains
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.notes_app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

### 3.8 Create Environment Files

**Create .env:**

```bash
# Public URL (update this when using ngrok or in production)
# This URL is used in widgets to call the MCP server
PUBLIC_URL=http://localhost:8000

# ngrok token (get from ngrok.com)
# Sign up at https://ngrok.com to get your token
NGROK_AUTHTOKEN=your_token_here
```

**What each variable does:**
- `PUBLIC_URL`: The public URL where your server is accessible (localhost for development, ngrok URL for ChatGPT testing, production URL for deployment)
- `NGROK_AUTHTOKEN`: Your ngrok authentication token (needed to create tunnels)

**Create .env.example:**

```bash
# Public URL for the application
PUBLIC_URL=http://localhost:8000

# ngrok authentication token
# Get yours at https://ngrok.com
NGROK_AUTHTOKEN=
```

**What this is:**
- Template file showing what environment variables are needed
- Committed to git (unlike `.env` which should be in `.gitignore`)
- Helps other developers know what to configure

### 3.9 Start the Server

```bash
# Start development server
just dev
```

You should see:
```
🚀 Starting development server...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Checkpoint**: Visit `http://localhost:8000/docs` - you won't see anything yet because we're using MCP, not REST API.

🎓 **You learned**: How to create a complete MCP server with tools but **without widgets yet** (we'll add those next!).

---

## Part 5: Creating Interactive Widgets - Evolutionary Approach

This is the most exciting part! We'll build widgets **gradually**, from simple to complex, so you understand each piece.

### 5.1 Widget Evolution Philosophy

Instead of showing you a complete 200-line widget, we'll evolve it:

1. **Version 1**: Static HTML (no data)
2. **Version 2**: Dynamic HTML with data
3. **Version 3**: Add basic styling
4. **Version 4**: Add interactivity (window.openai API)
5. **Version 5**: Final polished version

### 5.2 Understanding Widget Basics

Before we start coding, understand these concepts:

**What is a Widget?**
- HTML page displayed inside ChatGPT
- Has access to special `window.openai` API
- Can call MCP tools
- Can receive data from tool calls

**Widget Lifecycle:**
```
1. User asks ChatGPT → "show my notes"
2. ChatGPT calls list_notes tool
3. Tool returns structuredContent with notes data
4. ChatGPT requests widget HTML from ui://widget/notes-list.html
5. Widget generator creates HTML (can use the data)
6. ChatGPT displays widget in iframe
7. User interacts with widget (clicks delete button)
8. Widget calls MCP tool via window.openai.callTool()
9. Widget refreshes to show updated data
```

### 5.3 Widget Version 1: Static HTML

Let's start with the simplest possible widget. Add this to `mcp_server.py`:

```python
# ============================================================================
# Widget HTML Generators
# ============================================================================

def _get_notes_list_html_v1() -> str:
    """Widget Version 1: Static HTML

    This is the simplest version - just hardcoded HTML with no data.
    It helps us understand the basic structure.
    """
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Notes</title>
</head>
<body>
    <h1>My Notes</h1>
    <p>Note 1: Welcome to Notes App</p>
    <p>Note 2: MCP Integration</p>
</body>
</html>"""
```

**What this version has:**
- ✅ Valid HTML structure
- ✅ Hardcoded content
- ❌ No real data
- ❌ No styling
- ❌ No interactivity

**Why start here?**
- Understand the basic HTML structure
- See how widgets are just HTML
- Easy to debug

### 5.4 Widget Version 2: Dynamic HTML with Data

Now let's make it show real data from storage:

```python
def _get_notes_list_html_v2() -> str:
    """Widget Version 2: Dynamic HTML with real data

    Now we fetch notes from storage and display them.
    Still no styling or interactivity.
    """
    # Get notes from storage
    notes = storage.list()

    # Build HTML for each note
    notes_html = ""
    for note in notes:
        notes_html += f"""
        <div>
            <h3>{note.title}</h3>
            <p>{note.content}</p>
            <small>Created: {note.created_at}</small>
        </div>
        """

    # If no notes, show message
    if not notes:
        notes_html = "<p>No notes yet. Create one to get started!</p>"

    # Return complete HTML
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Notes</title>
</head>
<body>
    <h1>My Notes ({len(notes)})</h1>
    {notes_html}
</body>
</html>"""
```

**What this version has:**
- ✅ Valid HTML structure
- ✅ Real data from storage
- ✅ Shows count of notes
- ✅ Handles empty state
- ❌ No styling
- ❌ No interactivity

**What changed:**
- `storage.list()` - Fetches real notes
- Loop creates HTML for each note
- Uses Python f-strings to insert data
- Shows creation timestamp

**Security Note:**
Notice we just insert `{note.title}` directly. In production, you should escape HTML:
```python
safe_title = note.title.replace('<', '&lt;').replace('>', '&gt;')
```

### 5.5 Widget Version 3: Add Basic Styling

Now let's make it look good:

```python
def _get_notes_list_html_v3() -> str:
    """Widget Version 3: Add beautiful styling

    Now we add CSS to make it visually appealing.
    """
    notes = storage.list()

    notes_html = ""
    for note in notes:
        # Escape HTML to prevent XSS
        safe_title = note.title.replace('<', '&lt;').replace('>', '&gt;')
        safe_content = note.content.replace('<', '&lt;').replace('>', '&gt;')

        notes_html += f"""
        <div class="note-card">
            <h3>{safe_title}</h3>
            <p>{safe_content}</p>
            <small>Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}</small>
        </div>
        """

    if not notes:
        notes_html = """
        <div class="empty-state">
            <p>📝 No notes yet</p>
            <p>Create one to get started!</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Notes</title>
    <style>
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        /* Body styling */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        /* Page title */
        h1 {{
            color: white;
            margin-bottom: 20px;
            font-size: 28px;
        }}

        /* Note card styling */
        .note-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .note-card h3 {{
            color: #1a202c;
            margin-bottom: 8px;
        }}

        .note-card p {{
            color: #4a5568;
            line-height: 1.6;
            margin-bottom: 8px;
        }}

        .note-card small {{
            color: #a0aec0;
        }}

        /* Empty state */
        .empty-state {{
            background: white;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            color: #718096;
        }}
    </style>
</head>
<body>
    <h1>📝 My Notes ({len(notes)})</h1>
    {notes_html}
</body>
</html>"""
```

**What this version has:**
- ✅ Valid HTML structure
- ✅ Real data from storage
- ✅ Beautiful gradient background
- ✅ Card-based layout
- ✅ Professional typography
- ✅ HTML escaping for security
- ❌ No interactivity

**CSS Breakdown:**
- `*`: Resets default browser styles
- `body`: Gradient background, padding
- `.note-card`: White cards with shadow and rounded corners
- `.empty-state`: Centered message for no notes

**Design Principles:**
- Modern UI with gradients
- Card-based layout (popular pattern)
- System fonts for consistency
- Proper spacing and typography

### 5.6 Widget Version 4: Add Basic Interactivity

Now the exciting part - let's add a delete button:

```python
def _get_notes_list_html_v4() -> str:
    """Widget Version 4: Add interactivity with window.openai API

    Now we add delete buttons that call MCP tools.
    This shows how widgets can interact with your server.
    """
    notes = storage.list()

    notes_html = ""
    for note in notes:
        safe_title = note.title.replace('<', '&lt;').replace('>', '&gt;')
        safe_content = note.content.replace('<', '&lt;').replace('>', '&gt;')

        notes_html += f"""
        <div class="note-card">
            <div class="note-header">
                <h3>{safe_title}</h3>
                <button class="delete-btn" onclick="deleteNote('{note.id}')">🗑️</button>
            </div>
            <p>{safe_content}</p>
            <small>Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}</small>
        </div>
        """

    if not notes:
        notes_html = """
        <div class="empty-state">
            <p>📝 No notes yet</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Notes</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        h1 {{ color: white; margin-bottom: 20px; font-size: 28px; }}

        .note-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        /* NEW: Header with flexbox for title and button */
        .note-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
        }}

        .note-card h3 {{ color: #1a202c; flex: 1; }}
        .note-card p {{ color: #4a5568; line-height: 1.6; margin-bottom: 8px; }}
        .note-card small {{ color: #a0aec0; }}

        /* NEW: Delete button styling */
        .delete-btn {{
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background 0.2s;
        }}

        .delete-btn:hover {{
            background: #fee;
        }}

        .empty-state {{
            background: white;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>📝 My Notes ({len(notes)})</h1>
    {notes_html}

    <script>
        // This is the magic! window.openai API lets widgets call MCP tools
        async function deleteNote(noteId) {{
            // Show confirmation dialog
            if (!confirm('Are you sure you want to delete this note?')) {{
                return;
            }}

            try {{
                // Call the delete_note MCP tool
                const result = await window.openai.callTool({{
                    name: 'delete_note',  // Tool name from mcp_server.py
                    arguments: {{
                        noteId: noteId  // Tool arguments
                    }}
                }});

                // Refresh the widget to show updated list
                if (window.openai.refreshWidget) {{
                    await window.openai.refreshWidget();
                }}
            }} catch (error) {{
                console.error('Failed to delete note:', error);
                alert('Failed to delete note. Please try again.');
            }}
        }}
    </script>
</body>
</html>"""
```

**What this version has:**
- ✅ Valid HTML structure
- ✅ Real data from storage
- ✅ Beautiful styling
- ✅ Delete button on each note
- ✅ Calls MCP tool via `window.openai.callTool()`
- ✅ Refreshes widget after deletion
- ✅ Error handling

**New Concepts:**

**1. window.openai.callTool()**
```javascript
await window.openai.callTool({
    name: 'delete_note',  // Which tool to call
    arguments: {          // Tool arguments
        noteId: noteId
    }
})
```

This is **THE** key API for widget interactivity. It:
- Calls an MCP tool from JavaScript
- Returns a promise (use await)
- Passes arguments to the tool
- Returns the tool result

**2. window.openai.refreshWidget()**
```javascript
await window.openai.refreshWidget()
```

This tells ChatGPT to:
- Re-fetch the widget HTML from your server
- Re-render the widget with fresh data
- Update the display

**3. Event Flow:**
```
User clicks delete → deleteNote('123') called →
window.openai.callTool({name: 'delete_note', ...}) →
MCP server processes delete →
window.openai.refreshWidget() →
ChatGPT re-fetches widget HTML →
Widget re-renders with updated notes
```

### 5.7 Widget Version 5: Final Polished Version

Let's add the final touches - hover effects, better transitions, and loading states:

```python
def _get_notes_list_html() -> str:
    """Widget Final Version: Production-ready with all features

    This is the polished version with:
    - Beautiful design
    - Smooth animations
    - Error handling
    - Loading states
    - Accessibility
    """
    notes = storage.list()

    notes_html = ""
    for note in notes:
        safe_title = note.title.replace('<', '&lt;').replace('>', '&gt;')
        safe_content = note.content.replace('<', '&lt;').replace('>', '&gt;')

        notes_html += f"""
        <div class="note-card" data-note-id="{note.id}">
            <div class="note-header">
                <h3 class="note-title">{safe_title}</h3>
                <button class="delete-btn" onclick="deleteNote('{note.id}')" aria-label="Delete note">🗑️</button>
            </div>
            <div class="note-content">{safe_content}</div>
            <div class="note-meta">
                <small>Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}</small>
                {f'<small>Updated: {note.updated_at.strftime("%Y-%m-%d %H:%M")}</small>' if note.updated_at != note.created_at else ''}
            </div>
        </div>
        """

    if not notes:
        notes_html = """
        <div class="empty-state">
            <p class="empty-icon">📝</p>
            <p class="empty-text">No notes yet</p>
            <p class="empty-subtext">Ask ChatGPT to create your first note!</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Notes</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}

        h2 {{
            color: white;
            margin-bottom: 20px;
            font-size: 28px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        /* Note card with hover effect */
        .note-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .note-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}

        .note-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
        }}

        .note-title {{
            color: #1a202c;
            font-size: 20px;
            font-weight: 600;
            flex: 1;
        }}

        .delete-btn {{
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background 0.2s;
            opacity: 0.6;
        }}

        .delete-btn:hover {{
            background: #fee;
            opacity: 1;
        }}

        .note-content {{
            color: #4a5568;
            line-height: 1.6;
            margin-bottom: 12px;
            white-space: pre-wrap;
        }}

        .note-meta {{
            display: flex;
            gap: 16px;
            color: #a0aec0;
            font-size: 12px;
        }}

        /* Empty state */
        .empty-state {{
            background: white;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
        }}

        .empty-icon {{
            font-size: 48px;
            margin-bottom: 16px;
        }}

        .empty-text {{
            font-size: 18px;
            color: #718096;
            margin-bottom: 8px;
        }}

        .empty-subtext {{
            font-size: 14px;
            color: #a0aec0;
        }}

        /* Loading state */
        .loading {{
            opacity: 0.5;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>📝 My Notes</h2>
        <div id="notes-container">
            {notes_html}
        </div>
    </div>

    <script>
        async function deleteNote(noteId) {{
            if (!confirm('Are you sure you want to delete this note?')) {{
                return;
            }}

            // Get the note card element
            const noteCard = document.querySelector(`[data-note-id="${{noteId}}"]`);

            // Add loading state
            if (noteCard) {{
                noteCard.classList.add('loading');
            }}

            try {{
                // Call the delete_note tool via window.openai
                const result = await window.openai.callTool({{
                    name: 'delete_note',
                    arguments: {{
                        noteId: noteId
                    }}
                }});

                console.log('Delete result:', result);

                // Refresh the widget to show updated list
                if (window.openai.refreshWidget) {{
                    await window.openai.refreshWidget();
                }}
            }} catch (error) {{
                console.error('Failed to delete note:', error);
                alert('Failed to delete note. Please try again.');

                // Remove loading state on error
                if (noteCard) {{
                    noteCard.classList.remove('loading');
                }}
            }}
        }}

        // Listen for widget refresh events
        if (window.openai && window.openai.addEventListener) {{
            window.openai.addEventListener('refresh', () => {{
                console.log('Widget refreshing...');
            }});
        }}

        // Log widget load
        console.log('Notes widget loaded with {{len(notes)}} notes');
    </script>
</body>
</html>"""
```

**What's NEW in final version:**

1. **Loading States**: Card becomes semi-transparent during delete
2. **Hover Effects**: Card lifts up slightly on hover
3. **Better Typography**: Proper font weights and sizes
4. **Accessibility**: `aria-label` on buttons
5. **Event Listeners**: Logs widget refresh events
6. **Updated Timestamp**: Shows if note was edited
7. **Console Logging**: Helps with debugging

🎓 **You learned**:
- How to build widgets evolutionarily (simple → complex)
- The importance of each piece (data, styling, interactivity)
- How `window.openai` API works
- How to add polish (animations, loading states)

---

## Continuing the Tutorial...

The tutorial continues with these sections (refer back to Part 1):

- **Part 4**: Testing with MCP Inspector
- **Part 5.8**: Add Resource Handlers
- **Part 6**: Connecting to ChatGPT
- **Part 7**: Production Deployment

### 5.8 Add Resource Handlers

Now we need to tell MCP how to serve our widgets. Add this to `mcp_server.py`:

```python
# ============================================================================
# MCP Resource Handlers (for widgets)
# ============================================================================

@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    """List all widget resources

    This tells ChatGPT what widgets are available.
    """
    return [
        types.Resource(
            name="Notes List Widget",
            title="Notes List",
            uri=WIDGETS_URI,
            description="Interactive display of all notes with delete functionality",
            mimeType=MIME_TYPE,
        ),
        types.Resource(
            name="Notes Statistics Widget",
            title="Notes Stats",
            uri=STATS_WIDGET_URI,
            description="Statistics dashboard for your notes",
            mimeType=MIME_TYPE,
        ),
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    """Handle resource read requests for widget HTML

    When ChatGPT wants to display a widget, it calls this function
    with the widget URI. We generate the HTML and return it.
    """
    uri = str(req.params.uri)

    if uri == WIDGETS_URI:
        # Generate notes list widget HTML
        html = _get_notes_list_html()
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[
                    types.TextResourceContents(
                        uri=WIDGETS_URI,
                        mimeType=MIME_TYPE,
                        text=html,
                    )
                ]
            )
        )

    elif uri == STATS_WIDGET_URI:
        # Generate statistics widget HTML
        html = _get_stats_widget_html()
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[
                    types.TextResourceContents(
                        uri=STATS_WIDGET_URI,
                        mimeType=MIME_TYPE,
                        text=html,
                    )
                ]
            )
        )

    else:
        # Unknown resource
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {uri}"},
            )
        )


# Register the resource read handler
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource
```

**What this does:**
- `list_resources()`: Tells ChatGPT what widgets exist
- `_handle_read_resource()`: Generates widget HTML when requested
- Routes based on URI to the correct widget generator

### 5.9 Create Statistics Widget

For completeness, let's add a simple stats widget:

```python
def _get_stats_widget_html() -> str:
    """Generate HTML for the statistics widget"""
    stats = storage.get_stats()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notes Statistics</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            min-height: 100vh;
        }}

        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            max-width: 600px;
            margin: 0 auto;
        }}

        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-4px);
        }}

        .stat-value {{
            font-size: 48px;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 8px;
        }}

        .stat-label {{
            color: #718096;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-value">{stats.total}</div>
            <div class="stat-label">Total Notes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.created_today}</div>
            <div class="stat-label">Created Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.updated_today}</div>
            <div class="stat-label">Updated Today</div>
        </div>
    </div>
</body>
</html>"""
```

**Design notes:**
- Different gradient (pink/yellow) to differentiate from notes list
- Grid layout for stats cards
- Large numbers for easy scanning
- Hover effect for interactivity

---

## Summary of Part 2

🎉 **Congratulations!** You've learned:

### Widget Development (Evolutionary Approach)

1. **Version 1**: Static HTML - Understanding structure
2. **Version 2**: Dynamic data - Fetching from storage
3. **Version 3**: Beautiful styling - CSS and design
4. **Version 4**: Interactivity - window.openai API
5. **Version 5**: Polish - Animations and UX

### Key APIs Learned

- `window.openai.callTool()` - Call MCP tools from widgets
- `window.openai.refreshWidget()` - Refresh widget display
- `window.openai.addEventListener()` - Listen to widget events

### Architecture Understanding

- How MCP tools and widgets work together
- How data flows from tools to widgets
- How widgets call tools back
- Resource handlers for serving widgets

---

## Next Steps

Continue with the main tutorial for:

- **Part 4**: Testing with MCP Inspector
- **Part 6**: Connecting to ChatGPT
- **Part 7**: Production Deployment

**Remember**: The evolutionary approach helps you understand **why** each piece exists, not just **what** it does.

Happy building! 🚀
