# Tutorial: Build Your First MCP Application - From Rookie to Expert

> **Document Type**: Tutorial (Learning-oriented)
> **Objective**: Learn to create a production-ready MCP application integrated with ChatGPT
> **Estimated Time**: 2-3 hours
> **Level**: Beginner to Advanced

## Learning Objectives

By the end of this tutorial, you will understand:

1. **What is the Model Context Protocol (MCP)** - The communication standard between AI assistants and external tools
2. **How MCP servers communicate with ChatGPT** - JSON-RPC protocol, tools, and resources
3. **How to create and register tools** - Define callable functions for ChatGPT
4. **How to test with MCP Inspector** - Validate your server before ChatGPT integration
5. **How to connect your server to ChatGPT** - OpenAI Apps SDK integration
6. **How to create HTML widgets for ChatGPT** - Build interactive visual interfaces
7. **How to use `window.openai` API** - Enable widgets to call tools from JavaScript
8. **How to return structured content from tools** - Pass data to widgets
9. **How widgets receive and display data** - Render dynamic content
10. **How widgets can call tools back** - Interactive widget-to-tool communication
11. **Delivery and Deploy on ChatGPT** - Production deployment strategies

## Introduction

In this tutorial, you'll build a **Notes Application** that integrates with ChatGPT using the Model Context Protocol (MCP). You'll start from scratch, creating a Nix development environment, implementing MCP tools, building interactive widgets, and finally deploying to production.

**What you'll build**: A complete notes application where users can create, view, update, and delete notes through ChatGPT, with beautiful interactive widgets displayed directly in the chat interface.

## Table of Contents

- [Part 1: Understanding MCP](#part-1-understanding-mcp)
- [Part 2: Setting Up with Nix](#part-2-setting-up-with-nix)
- [Part 3: Building the MCP Server](#part-3-building-the-mcp-server)
- [Part 4: Testing with MCP Inspector](#part-4-testing-with-mcp-inspector)
- [Part 5: Creating Interactive Widgets](#part-5-creating-interactive-widgets)
- [Part 6: Connecting to ChatGPT](#part-6-connecting-to-chatgpt)
- [Part 7: Production Deployment](#part-7-production-deployment)

---

## Part 1: Understanding MCP

### 1.1 What is the Model Context Protocol?

The **Model Context Protocol (MCP)** is an open standard that enables AI assistants like ChatGPT to securely interact with external data sources and tools. Think of it as a universal translator between AI models and your applications.

**Key Concepts**:

- **MCP Server**: Your application that exposes tools and data
- **MCP Client**: ChatGPT acts as the client, calling your tools
- **Tools**: Functions that ChatGPT can execute (like creating a note)
- **Resources**: Data or UI that ChatGPT can read (like widget HTML)
- **Transport**: How messages are sent (we'll use HTTP)

### 1.2 How MCP Communication Works

```
┌─────────────┐                    ┌─────────────┐
│   ChatGPT   │                    │  Your MCP   │
│   (Client)  │                    │   Server    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. "Create a note..."           │
       ├─────────────────────────────────>│
       │                                  │
       │  2. JSON-RPC: tools/list         │
       ├─────────────────────────────────>│
       │                                  │
       │  3. Returns: [create_note, ...]  │
       │<─────────────────────────────────┤
       │                                  │
       │  4. JSON-RPC: tools/call         │
       │     name: "create_note"          │
       │     args: {title: "...", ...}    │
       ├─────────────────────────────────>│
       │                                  │
       │  5. Result + Widget HTML         │
       │<─────────────────────────────────┤
       │                                  │
       │  6. Display widget to user       │
       └──────────────────────────────────┘
```

**The Flow**:

1. User asks ChatGPT to perform an action
2. ChatGPT discovers available tools via `tools/list`
3. ChatGPT calls a tool via `tools/call` with arguments
4. Your server processes the request and returns results
5. ChatGPT can request widget HTML via `resources/read`
6. Widget is displayed to the user in ChatGPT

### 1.3 JSON-RPC 2.0 Protocol

MCP uses JSON-RPC 2.0 for all communication. Here's an example:

**Request** (ChatGPT → Your Server):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_note",
    "arguments": {
      "title": "Shopping List",
      "content": "Milk, Eggs, Bread"
    }
  }
}
```

**Response** (Your Server → ChatGPT):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Note created successfully"
      }
    ],
    "structuredContent": {
      "note": {
        "id": "123",
        "title": "Shopping List",
        "content": "Milk, Eggs, Bread"
      }
    }
  }
}
```

🎓 **You learned**: MCP is a standardized protocol using JSON-RPC 2.0 for AI-to-application communication.

---

## Part 2: Setting Up with Nix

### 2.1 Why Nix?

Nix provides **reproducible development environments**. Everyone on your team gets the exact same tools and versions. No more "works on my machine" issues.

### 2.2 Prerequisites

- **Nix with flakes enabled** - [Install Nix](https://nixos.org/download.html)
- **Code editor** (VS Code, Vim, etc.)
- **Terminal**
- **ngrok account** (free) - [Sign up at ngrok.com](https://ngrok.com)

### 2.3 Enable Nix Flakes

If you haven't enabled flakes yet:

```bash
# Create Nix config directory
mkdir -p ~/.config/nix

# Enable flakes
cat > ~/.config/nix/nix.conf <<EOF
experimental-features = nix-command flakes
EOF
```

### 2.4 Create Your Project Directory

```bash
# Create project directory
mkdir my-notes-app
cd my-notes-app

# Initialize git
git init
```

### 2.5 Create the Nix Flake

Create `flake.nix` in your project root:

```nix
{
  description = "Notes App with MCP Integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;  # For ngrok
          };
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python environment
            python311
            python311Packages.pip
            python311Packages.virtualenv

            # Package managers
            uv

            # Task runner
            just

            # Development tools
            ngrok
            curl
            jq

            # Git
            git
          ];

          shellHook = ''
            echo "🚀 Notes App Development Environment"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Python: $(python --version)"
            echo "uv: $(uv --version)"
            echo "just: $(just --version)"
            echo "ngrok: $(ngrok --version | head -n1)"
            echo ""
            echo "Available commands:"
            echo "  just init    - Initialize the project"
            echo "  just dev     - Start development server"
            echo "  just test    - Run tests"
            echo "  just tunnel  - Start ngrok tunnel"
            echo ""

            # Create .envrc for direnv if available
            if command -v direnv &> /dev/null; then
              echo "use flake" > .envrc
              direnv allow
            fi
          '';
        };
      }
    );
}
```

### 2.6 Enter the Nix Development Shell

```bash
nix develop
```

You should see the welcome message and all tools available.

🎓 **You learned**: How to create a Nix flake for reproducible development environments.

### 2.7 Create the Justfile

Create a `justfile` for common tasks:

```just
# Default Python version
python := "python3.11"

# Initialize the project
init:
    @echo "📦 Initializing project..."
    uv venv
    @echo "✅ Virtual environment created"
    @echo "Run: source .venv/bin/activate"

# Install dependencies
install:
    @echo "📦 Installing dependencies..."
    uv sync

# Start development server
dev:
    @echo "🚀 Starting development server..."
    uv run uvicorn src.notes_app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
    @echo "🧪 Running tests..."
    uv run pytest tests/ -v

# Run MCP Inspector
inspect:
    @echo "🔍 Starting MCP Inspector..."
    @echo "Make sure the server is running on port 8000"
    npx @modelcontextprotocol/inspector http://localhost:8000/mcp

# Start ngrok tunnel
tunnel:
    @echo "🌐 Starting ngrok tunnel..."
    ngrok http 8000

# Clean generated files
clean:
    @echo "🧹 Cleaning generated files..."
    rm -rf .venv __pycache__ .pytest_cache .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Format code
format:
    @echo "✨ Formatting code..."
    uv run ruff format .

# Lint code
lint:
    @echo "🔍 Linting code..."
    uv run ruff check .

# Show environment info
info:
    @echo "📊 Environment Information"
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "Python: $(which python)"
    @echo "Python version: $(python --version)"
    @echo "uv version: $(uv --version)"
    @echo "Working directory: $(pwd)"
```

🎓 **You learned**: How to create a justfile for automating common development tasks.

---

## Part 3: Building the MCP Server

### 3.1 Create Project Structure

```bash
# Create source directories
mkdir -p src/notes_app
touch src/notes_app/__init__.py

# Create tests directory
mkdir -p tests
touch tests/__init__.py

# Create docs
mkdir -p docs
```

### 3.2 Create pyproject.toml

Create `pyproject.toml` with dependencies:

```toml
[project]
name = "notes-app"
version = "0.1.0"
description = "A notes application with MCP integration for ChatGPT"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "mcp[fastapi]>=0.1.0",
    "pydantic>=2.9.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "ruff>=0.6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

### 3.3 Install Dependencies

```bash
# Initialize virtual environment
just init
source .venv/bin/activate

# Install all dependencies
just install
```

✅ **Checkpoint**: You should see all dependencies installed without errors.

### 3.4 Create Data Models

Create `src/notes_app/models.py`:

```python
"""Data models for the Notes application"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Note(BaseModel):
    """A single note with title, content, and metadata"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Meeting Notes",
                "content": "Discussed Q4 roadmap and priorities",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )

    id: str = Field(..., description="Unique identifier (UUID)")
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., description="Note content (markdown supported)")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )


class NoteCreate(BaseModel):
    """Request model for creating a new note"""

    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., description="Note content")


class NoteUpdate(BaseModel):
    """Request model for updating an existing note"""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Note title")
    content: Optional[str] = Field(None, description="Note content")


class NoteStats(BaseModel):
    """Statistics about notes"""

    total: int = Field(..., description="Total number of notes")
    created_today: int = Field(0, description="Notes created today")
    updated_today: int = Field(0, description="Notes updated today")
```

🎓 **You learned**: How to use Pydantic v2 to define type-safe data models with validation.

### 3.5 Create Storage Layer

Create `src/notes_app/storage.py`:

```python
"""In-memory storage for notes with CRUD operations"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from .models import Note, NoteCreate, NoteUpdate, NoteStats


class NotesStorage:
    """Simple in-memory storage for notes

    In production, replace this with a database like PostgreSQL or SQLite.
    """

    def __init__(self):
        self._notes: Dict[str, Note] = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Add sample notes for demonstration"""
        sample_notes = [
            NoteCreate(
                title="Welcome to Notes App",
                content="This is your first note. You can create, read, update, and delete notes using ChatGPT!"
            ),
            NoteCreate(
                title="MCP Integration",
                content="This app uses the Model Context Protocol to integrate with ChatGPT. Tools are defined in mcp_server.py."
            ),
        ]
        for note_create in sample_notes:
            self.create(note_create)

    def create(self, note_create: NoteCreate) -> Note:
        """Create a new note"""
        note = Note(
            id=str(uuid4()),
            title=note_create.title,
            content=note_create.content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self._notes[note.id] = note
        return note

    def list(self) -> List[Note]:
        """List all notes, sorted by creation date (newest first)"""
        return sorted(
            self._notes.values(),
            key=lambda n: n.created_at,
            reverse=True
        )

    def get(self, note_id: str) -> Optional[Note]:
        """Get a specific note by ID"""
        return self._notes.get(note_id)

    def update(self, note_id: str, note_update: NoteUpdate) -> Optional[Note]:
        """Update an existing note"""
        note = self._notes.get(note_id)
        if not note:
            return None

        # Update fields if provided
        if note_update.title is not None:
            note.title = note_update.title
        if note_update.content is not None:
            note.content = note_update.content

        note.updated_at = datetime.utcnow()
        return note

    def delete(self, note_id: str) -> bool:
        """Delete a note by ID"""
        if note_id in self._notes:
            del self._notes[note_id]
            return True
        return False

    def get_stats(self) -> NoteStats:
        """Get statistics about notes"""
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)

        created_today = sum(
            1 for note in self._notes.values()
            if note.created_at >= today_start
        )

        updated_today = sum(
            1 for note in self._notes.values()
            if note.updated_at >= today_start
        )

        return NoteStats(
            total=len(self._notes),
            created_today=created_today,
            updated_today=updated_today
        )


# Global singleton instance
storage = NotesStorage()
```

🎓 **You learned**: How to implement a repository pattern for data access with in-memory storage.

### 3.6 Create the MCP Server

Create `src/notes_app/mcp_server.py`:

```python
"""MCP Server implementation for Notes App

This module defines the MCP tools and resources that ChatGPT can interact with.
"""

import os
from typing import Any, Dict, List

import mcp.types as types
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from .models import NoteCreate, NoteUpdate
from .storage import storage

# Load environment variables
load_dotenv()

# Get public URL for widgets (from ngrok or deployment)
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")

# Initialize MCP server
mcp = FastMCP(
    name="notes-app",
    stateless_http=True,
)

# Widget configuration
WIDGETS_URI = "ui://widget/notes-list.html"
STATS_WIDGET_URI = "ui://widget/notes-stats.html"
MIME_TYPE = "text/html+skybridge"


# ============================================================================
# MCP Tool Input Schemas (using Pydantic for validation)
# ============================================================================

class CreateNoteInput(BaseModel):
    """Input schema for creating a note"""
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


# ============================================================================
# Widget HTML Generators
# ============================================================================

def _get_notes_list_html() -> str:
    """Generate HTML for the notes list widget

    This widget displays all notes in a card layout and allows users
    to interact with notes via the window.openai API.
    """
    notes = storage.list()

    notes_html = ""
    for note in notes:
        # Escape HTML in content
        safe_title = note.title.replace('<', '&lt;').replace('>', '&gt;')
        safe_content = note.content.replace('<', '&lt;').replace('>', '&gt;')

        notes_html += f"""
        <div class="note-card" data-note-id="{note.id}">
            <div class="note-header">
                <h3 class="note-title">{safe_title}</h3>
                <button class="delete-btn" onclick="deleteNote('{note.id}')">🗑️</button>
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
            <p>📝 No notes yet</p>
            <p>Ask ChatGPT to create your first note!</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
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
        }}

        .delete-btn:hover {{
            background: #fee;
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

        .empty-state {{
            background: white;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            color: #718096;
        }}

        .empty-state p:first-child {{
            font-size: 48px;
            margin-bottom: 16px;
        }}

        .empty-state p:last-child {{
            font-size: 16px;
            color: #a0aec0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>📝 My Notes</h2>
        {notes_html}
    </div>

    <script>
        // The window.openai API allows widgets to call MCP tools
        async function deleteNote(noteId) {{
            if (!confirm('Are you sure you want to delete this note?')) {{
                return;
            }}

            try {{
                // Call the delete_note tool via window.openai
                const result = await window.openai.callTool({{
                    name: 'delete_note',
                    arguments: {{
                        noteId: noteId
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

        // Listen for widget refresh events
        if (window.openai && window.openai.addEventListener) {{
            window.openai.addEventListener('refresh', () => {{
                // Widget will be automatically reloaded
                console.log('Widget refreshing...');
            }});
        }}
    </script>
</body>
</html>"""


def _get_stats_widget_html() -> str:
    """Generate HTML for the statistics widget"""
    stats = storage.get_stats()

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notes Statistics</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
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


# ============================================================================
# MCP Protocol Handlers
# ============================================================================

@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List all available MCP tools

    This is called by ChatGPT to discover what tools are available.
    """
    return [
        types.Tool(
            name="create_note",
            title="Create Note",
            description="Create a new note with a title and content",
            inputSchema={
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
                "additionalProperties": False,
            },
            _meta={
                "openai/widgetAccessible": True,
            },
        ),
        types.Tool(
            name="list_notes",
            title="List Notes",
            description="List all notes with an interactive widget",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            _meta={
                "openai/outputTemplate": WIDGETS_URI,
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True,
            },
        ),
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
                "openai/widgetAccessible": True,
            },
        ),
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
                "openai/outputTemplate": STATS_WIDGET_URI,
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True,
            },
        ),
    ]


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool call requests from ChatGPT

    This is called when ChatGPT executes a tool.
    """
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    # CREATE NOTE
    if tool_name == "create_note":
        payload = CreateNoteInput.model_validate(arguments)
        note_create = NoteCreate(title=payload.title, content=payload.content)
        note = storage.create(note_create)

        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"✅ Created note: **{note.title}**",
                    )
                ],
                structuredContent={
                    "note": note.model_dump(mode='json')
                },
            )
        )

    # LIST NOTES
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

    # GET NOTE
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
                    isError=True,
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

    # UPDATE NOTE
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

    # DELETE NOTE
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

    # GET STATISTICS
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

    # UNKNOWN TOOL
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


# ============================================================================
# MCP Resource Handlers (for widgets)
# ============================================================================

@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    """List all widget resources"""
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
    """Handle resource read requests for widget HTML"""
    uri = str(req.params.uri)

    if uri == WIDGETS_URI:
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
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {uri}"},
            )
        )


# Register the resource read handler
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource
```

🎓 **You learned**:
- How to define MCP tools with JSON schemas
- How to handle tool calls and return structured content
- How to create and serve HTML widgets
- How to use the `window.openai` API for widget interactivity

### 3.7 Create the Main Application

Create `src/notes_app/main.py`:

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

### 3.8 Create Environment File

Create `.env`:

```bash
# Public URL (update this when using ngrok or in production)
PUBLIC_URL=http://localhost:8000

# ngrok token (get from ngrok.com)
NGROK_AUTHTOKEN=your_token_here
```

Create `.env.example`:

```bash
# Public URL for the application
PUBLIC_URL=http://localhost:8000

# ngrok authentication token
NGROK_AUTHTOKEN=
```

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
```

✅ **Checkpoint**: Visit `http://localhost:8000/docs` to see the auto-generated API documentation.

🎓 **You learned**: How to create a complete MCP server with tools, resources, and widgets.

---

## Part 4: Testing with MCP Inspector

### 4.1 What is MCP Inspector?

**MCP Inspector** is a debugging tool that lets you test your MCP server before integrating with ChatGPT. It provides a UI to:

- View available tools
- Call tools with test arguments
- See responses and errors
- Debug widget rendering

### 4.2 Install MCP Inspector

The MCP Inspector is an npm package. Make sure Node.js is installed, then:

```bash
# Run directly with npx (no installation needed)
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

### 4.3 Using MCP Inspector

The inspector will open in your browser at `http://localhost:5173`.

**1. View Tools**

You should see all 6 tools listed:
- create_note
- list_notes
- get_note
- update_note
- delete_note
- get_stats

**2. Test create_note**

Click on "create_note", fill in the form:
```json
{
  "title": "Test Note",
  "content": "This is a test note from MCP Inspector"
}
```

Click "Call Tool" and you should see:
```json
{
  "content": [
    {
      "type": "text",
      "text": "✅ Created note: **Test Note**"
    }
  ],
  "structuredContent": {
    "note": {
      "id": "...",
      "title": "Test Note",
      "content": "This is a test note from MCP Inspector",
      "created_at": "...",
      "updated_at": "..."
    }
  }
}
```

**3. Test list_notes**

Click on "list_notes" and call it with empty arguments `{}`.

You should see the list of notes in `structuredContent`.

**4. View Resources**

Click on the "Resources" tab to see available widgets:
- Notes List Widget
- Notes Statistics Widget

Click on "Notes List Widget" to see the rendered HTML.

**5. Debug Widgets**

The inspector shows the raw HTML and also renders it in an iframe. This helps you debug styling and JavaScript issues.

✅ **Checkpoint**: You should be able to call all tools and view all widgets in the MCP Inspector.

🎓 **You learned**: How to use MCP Inspector to test your server before ChatGPT integration.

---

## Part 5: Creating Interactive Widgets

### 5.1 Understanding Widget Architecture

Widgets are HTML pages with special capabilities:

```
┌─────────────────────────────────────┐
│         ChatGPT Interface            │
│  ┌───────────────────────────────┐  │
│  │   Your Widget (HTML/CSS/JS)   │  │
│  │                               │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  window.openai API      │  │  │
│  │  │  - callTool()           │  │  │
│  │  │  - refreshWidget()      │  │  │
│  │  │  - addEventListener()   │  │  │
│  │  └─────────────────────────┘  │  │
│  │           ↓                   │  │
│  │    Calls MCP Tools            │  │
│  └───────────────────────────────┘  │
│                ↓                     │
│         Updates Display              │
└─────────────────────────────────────┘
```

### 5.2 The window.openai API

When your widget is rendered in ChatGPT, you have access to `window.openai`:

```javascript
// Call an MCP tool from your widget
const result = await window.openai.callTool({
    name: 'delete_note',
    arguments: {
        noteId: '123'
    }
});

// Refresh the widget (re-fetches HTML from server)
await window.openai.refreshWidget();

// Listen for events
window.openai.addEventListener('refresh', () => {
    console.log('Widget is being refreshed');
});
```

### 5.3 Returning Structured Content

When a tool is called, you can return both text content (for ChatGPT to display in chat) and structured content (data for widgets):

```python
return types.ServerResult(
    types.CallToolResult(
        # Text content - shown in chat
        content=[
            types.TextContent(
                type="text",
                text="✅ Created note: **Test Note**",
            )
        ],
        # Structured content - passed to widgets
        structuredContent={
            "note": {
                "id": "123",
                "title": "Test Note",
                "content": "Note content"
            }
        },
    )
)
```

### 5.4 Widget Receives Data

When ChatGPT renders a widget, it can access the structured content from the tool that triggered it:

```javascript
// Widget HTML has access to tool results
<script>
    // The structured content is available via window.openai
    window.openai.getToolResult().then(result => {
        console.log(result.structuredContent.note);
    });
</script>
```

### 5.5 Complete Widget Interaction Flow

Let's trace a complete interaction:

1. **User**: "Show me my notes"
2. **ChatGPT**: Calls `list_notes` tool
3. **Your server**: Returns text + structured content
4. **ChatGPT**: Displays text in chat and renders widget
5. **Widget**: Shows notes list with delete buttons
6. **User**: Clicks delete button in widget
7. **Widget JavaScript**: Calls `window.openai.callTool({name: 'delete_note', ...})`
8. **Your server**: Processes delete and returns success
9. **Widget JavaScript**: Calls `window.openai.refreshWidget()`
10. **ChatGPT**: Re-fetches widget HTML and updates display

🎓 **You learned**:
- How widgets use the `window.openai` API
- How tools return structured content
- How widgets receive and display data
- How widgets can call tools back for interactivity

---

## Part 6: Connecting to ChatGPT

### 6.1 Expose Your Server with ngrok

ChatGPT needs to access your server over the internet. We'll use ngrok:

```bash
# In your .env file, add your ngrok auth token
NGROK_AUTHTOKEN=your_token_from_ngrok_dashboard

# Start ngrok tunnel (in a separate terminal)
just tunnel
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

**Important**: Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`).

Update your `.env` file:
```bash
PUBLIC_URL=https://abc123.ngrok-free.app
```

Restart your server:
```bash
just dev
```

### 6.2 Register Your App on OpenAI Platform

1. Go to [platform.openai.com/apps](https://platform.openai.com/apps)
2. Click **"Create new app"**
3. Fill in details:
   - **Name**: "My Notes App"
   - **Description**: "A notes application with MCP integration"
   - **Icon**: (optional) Upload an icon

4. In the **"MCP Server"** section:
   - **Endpoint URL**: `https://YOUR-NGROK-URL/mcp`
   - Example: `https://abc123.ngrok-free.app/mcp`

5. Click **"Save"**

### 6.3 Test Connection

OpenAI will test your endpoint. You should see:
- ✅ "Connection successful"
- ✅ "Tools discovered: 6"
- ✅ "Resources discovered: 2"

If you see errors:
- Check that your server is running
- Check that ngrok is forwarding correctly
- Check that the URL includes `/mcp` at the end
- Check server logs for errors

### 6.4 Enable in ChatGPT

1. Go to [chat.openai.com](https://chat.openai.com)
2. Click your profile icon (bottom left)
3. Go to **Settings** → **Beta features**
4. Enable **"Apps"** if not already enabled
5. Start a new chat
6. Click the **"+"** button or app selector
7. Find **"My Notes App"** and enable it

### 6.5 Test in ChatGPT

Now test your app! Try these prompts:

**Create a note:**
```
Create a note with title "Shopping List" and content "Milk, Eggs, Bread, Coffee"
```

You should see:
- ChatGPT calls the `create_note` tool
- Success message: "✅ Created note: **Shopping List**"

**List notes:**
```
Show me all my notes
```

You should see:
- ChatGPT calls the `list_notes` tool
- A beautiful widget displaying all your notes
- Delete buttons on each note

**Delete from widget:**
- Click a delete button in the widget
- Confirm the deletion
- Watch the widget refresh automatically

**Get statistics:**
```
Show me my notes statistics
```

You should see:
- A colorful statistics widget
- Total notes, created today, updated today

✅ **Checkpoint**: You can create, view, and delete notes through ChatGPT!

🎓 **You learned**: How to connect your MCP server to ChatGPT and test the integration.

---

## Part 7: Production Deployment

### 7.1 Production Considerations

For production deployment, you need to consider:

1. **Persistent Storage**: Replace in-memory storage with a database
2. **Authentication**: Secure your MCP endpoint
3. **Hosting**: Deploy to a reliable platform
4. **CORS**: Restrict to OpenAI domains
5. **Error Handling**: Comprehensive logging and error handling
6. **Rate Limiting**: Prevent abuse
7. **Monitoring**: Track usage and errors

### 7.2 Database Integration

Replace in-memory storage with PostgreSQL:

```bash
# Add to pyproject.toml dependencies
dependencies = [
    # ... existing deps ...
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
]
```

Update `storage.py`:

```python
"""PostgreSQL storage implementation"""

from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/notes")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class NoteModel(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

Base.metadata.create_all(engine)

class NotesStorage:
    def create(self, note_create: NoteCreate) -> Note:
        db = SessionLocal()
        try:
            note = NoteModel(
                id=str(uuid4()),
                title=note_create.title,
                content=note_create.content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(note)
            db.commit()
            db.refresh(note)
            return Note.model_validate(note)
        finally:
            db.close()

    # Implement other methods similarly...
```

### 7.3 Deployment Options

#### Option A: Railway

[Railway](https://railway.app) is a simple platform for deploying Python apps:

1. Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.notes_app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. Create `Procfile`:
```
web: uvicorn src.notes_app.main:app --host 0.0.0.0 --port $PORT
```

3. Deploy:
```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Create project
railway init

# Add PostgreSQL
railway add -p postgresql

# Deploy
railway up
```

4. Set environment variables in Railway dashboard:
   - `PUBLIC_URL`: Your Railway app URL

#### Option B: Render

[Render](https://render.com) offers free tier for Python apps:

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: notes-app
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn src.notes_app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PUBLIC_URL
        sync: false

databases:
  - name: notes-db
    plan: starter
```

2. Generate `requirements.txt`:
```bash
uv pip compile pyproject.toml -o requirements.txt
```

3. Push to GitHub and connect to Render

#### Option C: Fly.io

[Fly.io](https://fly.io) supports Nix-based deployments:

1. Install Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Create `fly.toml`:
```toml
app = "my-notes-app"

[build]
  [build.args]
    PYTHON_VERSION = "3.11"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[deploy]
  release_command = "python -c 'print(\"Ready to deploy\")'"
```

3. Deploy:
```bash
fly launch
fly deploy
```

### 7.4 Secure Your Endpoint

Add authentication to your MCP endpoint:

```python
# src/notes_app/auth.py
import os
from fastapi import Header, HTTPException

API_KEY = os.getenv("MCP_API_KEY", "your-secret-key")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
```

Update `main.py`:

```python
from fastapi import Depends
from .auth import verify_api_key

# In your route
@app.post("/mcp", dependencies=[Depends(verify_api_key)])
async def mcp_endpoint():
    # ... existing code
```

Configure in OpenAI Apps:
- Add custom header: `X-API-Key: your-secret-key`

### 7.5 Production CORS

Restrict CORS to OpenAI domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chatgpt.com",
        "https://chat.openai.com",
        "https://*.openai.com",
    ],
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)
```

### 7.6 Monitoring and Logging

Add structured logging:

```python
import logging
from pythonjsonlogger import jsonlogger

# Setup JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Log tool calls
logger.info("tool_called", extra={
    "tool_name": tool_name,
    "arguments": arguments,
    "user_id": "...",
})
```

### 7.7 Update OpenAI App Configuration

1. Go to your app in OpenAI Platform
2. Update **MCP Server Endpoint** to your production URL:
   - `https://your-app.railway.app/mcp`
   - Or `https://your-app.onrender.com/mcp`
   - Or `https://your-app.fly.dev/mcp`

3. Add authentication headers if configured

4. Save and test

### 7.8 Production Checklist

- [ ] Database configured (PostgreSQL/MySQL)
- [ ] Environment variables set
- [ ] CORS restricted to OpenAI domains
- [ ] API authentication enabled
- [ ] Error logging configured
- [ ] Rate limiting implemented
- [ ] Health check endpoint added
- [ ] SSL/HTTPS enabled
- [ ] OpenAI app configuration updated
- [ ] Production testing completed

✅ **Checkpoint**: Your app is now running in production!

🎓 **You learned**: How to deploy an MCP application to production with proper security and monitoring.

---

## Summary

Congratulations! 🎉 You've built a complete MCP application from scratch and deployed it to production. Let's review what you learned:

### Core Concepts

1. ✅ **Model Context Protocol (MCP)**: Communication standard between AI and applications
2. ✅ **JSON-RPC 2.0**: Protocol for MCP messages
3. ✅ **Tools**: Callable functions that ChatGPT can execute
4. ✅ **Resources**: Data and UI that ChatGPT can read
5. ✅ **Widgets**: Interactive HTML interfaces in ChatGPT

### Development Skills

6. ✅ **Nix Flakes**: Reproducible development environments
7. ✅ **MCP Server Implementation**: Creating tools and resources
8. ✅ **MCP Inspector**: Testing and debugging
9. ✅ **Pydantic Models**: Type-safe data validation
10. ✅ **Storage Patterns**: Repository pattern for data access

### Integration Skills

11. ✅ **window.openai API**: Widget interactivity
12. ✅ **Structured Content**: Passing data to widgets
13. ✅ **Tool Callbacks**: Widgets calling tools
14. ✅ **OpenAI Apps SDK**: Connecting to ChatGPT

### Production Skills

15. ✅ **Database Integration**: PostgreSQL storage
16. ✅ **Deployment**: Railway, Render, Fly.io
17. ✅ **Security**: Authentication and CORS
18. ✅ **Monitoring**: Logging and error tracking

---

## Next Steps

Now that you have a solid foundation, you can:

### Enhance Your Notes App

1. **Rich Text Editor**: Add markdown rendering and WYSIWYG editing
2. **Tags & Categories**: Organize notes with tags
3. **Search**: Full-text search across notes
4. **Sharing**: Share notes with other users
5. **Attachments**: Support images and files
6. **Reminders**: Set reminders for notes

### Explore Advanced MCP Features

1. **Streaming Responses**: Real-time updates for long operations
2. **File Resources**: Serve files and documents
3. **Custom Prompts**: Guide ChatGPT's behavior
4. **Multi-user Support**: User authentication and isolation

### Build Other Applications

1. **Task Manager**: ToDo lists with projects and priorities
2. **CRM**: Customer relationship management
3. **Analytics Dashboard**: Data visualization
4. **Content Management**: Blog or documentation system
5. **API Integration**: Connect to external services

### Learn More

1. **Read the Guides**: Check `docs/GUIDE.md` for how-to guides
2. **Study the Explanation**: Read `docs/EXPLANATION.md` for deep dives
3. **Explore Examples**: Look at the ToDo app in this repository
4. **Join Community**: MCP Discord and GitHub discussions

---

## Resources

### Official Documentation

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [OpenAI Apps SDK Documentation](https://developers.openai.com/apps-sdk/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)

### Tools & Libraries

- [uv Package Manager](https://docs.astral.sh/uv/)
- [Just Command Runner](https://github.com/casey/just)
- [Nix Package Manager](https://nixos.org/)
- [ngrok Tunneling](https://ngrok.com/)

### Deployment Platforms

- [Railway](https://railway.app/)
- [Render](https://render.com/)
- [Fly.io](https://fly.io/)
- [Heroku](https://heroku.com/)

---

## Troubleshooting

### Server Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
uv sync

# Check for port conflicts
lsof -i :8000
```

### MCP Inspector Can't Connect

```bash
# Verify server is running
curl http://localhost:8000/mcp

# Check CORS configuration
# Should allow all origins for development
```

### ChatGPT Can't Connect

1. **Check ngrok**: Is the tunnel running?
2. **Check URL**: Does it include `/mcp`?
3. **Check logs**: Look for errors in your server
4. **Test endpoint**: Use curl to test the production URL

### Widgets Not Rendering

1. **Check MIME type**: Should be `text/html+skybridge`
2. **Check resource URI**: Should match `ui://widget/...`
3. **Check HTML**: Validate HTML syntax
4. **Check console**: Open browser console for JavaScript errors

### Tools Not Working

1. **Check tool schema**: Validate JSON schema
2. **Check input validation**: Pydantic models correct?
3. **Check handler**: Is the tool name handled in `_call_tool_request`?
4. **Check logs**: Look for validation errors

---

## Getting Help

If you encounter issues:

1. **Check Logs**: Always start with server logs
2. **Use MCP Inspector**: Debug locally first
3. **Review Documentation**: Check official MCP docs
4. **Search Issues**: GitHub issues for MCP and FastMCP
5. **Ask Community**: MCP Discord or forums

---

**Happy Building!** 🚀

You now have all the skills to build amazing MCP applications that integrate with ChatGPT. The possibilities are endless!

Remember:
- Start small and iterate
- Test thoroughly with MCP Inspector
- Monitor your production deployment
- Keep security in mind
- Have fun building!

---

*Tutorial last updated: 2024-01-15*
*MCP Specification: v1.0*
*FastMCP: v0.1.0*
