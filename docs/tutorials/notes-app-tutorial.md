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

### 2.5 Create the Nix Flake - Step by Step

Let's build the `flake.nix` file gradually, understanding each part:

**Step 1: Basic Structure**

Create `flake.nix` with the basic flake structure:

```nix
{
  description = "Notes App with MCP Integration";

  # Inputs: External dependencies for your flake
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    # This will define what your flake produces
    { };
}
```

**What this does:**
- `description`: Describes your project
- `inputs`: Declares dependencies (nixpkgs for packages, flake-utils for cross-platform support)
- `outputs`: Where we'll define our development environment (empty for now)

**Step 2: Add Platform Support**

Update the `outputs` section to support multiple platforms (Linux, macOS, etc.):

```nix
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      {
        # We'll define our development shell here
      }
    );
```

**What this does:**
- `eachDefaultSystem`: Creates outputs for all common platforms (x86_64-linux, aarch64-darwin, etc.)
- `pkgs`: Imports nixpkgs for the current system

**Step 3: Allow Unfree Packages (for ngrok)**

ngrok is proprietary software. We need to allow unfree packages:

```nix
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;  # Required for ngrok
          };
        };
      in
```

**What this does:**
- `allowUnfree = true`: Allows installation of proprietary software like ngrok

**Step 4: Define Development Tools**

Now let's add the development shell with all necessary tools:

```nix
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

            # Node.js for MCP Inspector
            nodejs_20

            # Git
            git
          ];
```

**What each tool does:**
- **python311**: Python 3.11 interpreter
- **pip & virtualenv**: Python package management
- **uv**: Fast Python package manager (alternative to pip)
- **just**: Task runner (like make, but simpler)
- **ngrok**: Tunneling tool to expose local server to internet
- **curl**: HTTP client for testing
- **jq**: JSON processor for debugging
- **nodejs_20**: Node.js 20 (needed for `npx` to run MCP Inspector)
- **git**: Version control

**Step 5: Add Welcome Message**

Add a shellHook that displays helpful information when entering the environment:

```nix
          shellHook = ''
            echo "🚀 Notes App Development Environment"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Python: $(python --version)"
            echo "uv: $(uv --version)"
            echo "just: $(just --version)"
            echo "ngrok: $(ngrok --version | head -n1)"
            echo "Node.js: $(node --version)"
            echo ""
            echo "Available commands:"
            echo "  just init    - Initialize the project"
            echo "  just dev     - Start development server"
            echo "  just test    - Run tests"
            echo "  just tunnel  - Start ngrok tunnel"
            echo "  just inspect - Open MCP Inspector"
            echo ""

            # Create .envrc for direnv if available
            if command -v direnv &> /dev/null; then
              echo "use flake" > .envrc
              direnv allow
            fi
          '';
```

**What this does:**
- Displays tool versions when you enter the shell
- Shows available `just` commands
- Automatically configures direnv if installed

**Complete flake.nix:**

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

            # Node.js for MCP Inspector
            nodejs_20

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
            echo "Node.js: $(node --version)"
            echo ""
            echo "Available commands:"
            echo "  just init    - Initialize the project"
            echo "  just dev     - Start development server"
            echo "  just test    - Run tests"
            echo "  just tunnel  - Start ngrok tunnel"
            echo "  just inspect - Open MCP Inspector"
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

You should see the welcome message with all tools available.

🎓 **You learned**:
- How to create a Nix flake for reproducible development environments
- What each development tool does and why we need it
- How to configure unfree packages
- How to add helpful shell hooks

### 2.7 Create pyproject.toml - Step by Step

The `pyproject.toml` file defines your Python project configuration and dependencies. Let's build it section by section:

**Step 1: Project Metadata**

Create `pyproject.toml` with basic project information:

```toml
[project]
name = "notes-app"
version = "0.1.0"
description = "A notes application with MCP integration for ChatGPT"
requires-python = ">=3.11"
```

**What this does:**
- `name`: Your project's name (used when installing)
- `version`: Current version number
- `description`: Brief description of the project
- `requires-python`: Minimum Python version required

**Step 2: Core Dependencies**

Add the main dependencies your app needs:

```toml
dependencies = [
    "fastapi>=0.115.0",      # Web framework for building APIs
    "uvicorn[standard]>=0.32.0",  # ASGI server to run FastAPI
    "mcp[fastapi]>=0.1.0",   # Model Context Protocol library
    "pydantic>=2.9.0",       # Data validation using type hints
    "python-dotenv>=1.0.0",  # Load environment variables from .env file
]
```

**What each dependency does:**
- **fastapi**: Modern web framework for building APIs with automatic OpenAPI documentation
- **uvicorn**: Lightning-fast ASGI server to run your FastAPI app
- **mcp[fastapi]**: Official MCP library with FastAPI integration
- **pydantic**: Data validation using Python type hints (required by FastAPI)
- **python-dotenv**: Loads configuration from `.env` files

**Step 3: Development Dependencies**

Add dependencies needed only during development:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",         # Testing framework
    "pytest-asyncio>=0.24.0", # Async support for pytest
    "httpx>=0.27.0",         # HTTP client for testing FastAPI
    "ruff>=0.6.0",           # Fast Python linter and formatter
]
```

**What each dev dependency does:**
- **pytest**: Python testing framework
- **pytest-asyncio**: Plugin to test async functions
- **httpx**: HTTP client to test FastAPI endpoints
- **ruff**: Fast linter and formatter (replaces black, isort, flake8)

**Step 4: Build System**

Define how to build your package:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**What this does:**
- Specifies that we use `hatchling` to build the package
- Modern build backend (alternative to setuptools)

**Step 5: Hatchling Build Configuration**

Configure hatchling to find your package:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/notes_app"]  # Tell hatchling where to find the package
```

**What this does:**
- `packages`: Specifies the directory path to your Python package
- This fixes the "Unable to determine which files to ship" error
- Required because our package is in `src/notes_app` instead of the project root

**Step 6: Pytest Configuration**

Configure pytest behavior:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Automatically detect and run async tests
testpaths = ["tests"]  # Where to find test files
```

**What this does:**
- `asyncio_mode = "auto"`: Pytest automatically handles async tests
- `testpaths`: Tells pytest where to look for tests

**Step 7: Ruff Configuration**

Configure the linter and formatter:

```toml
[tool.ruff]
line-length = 100      # Maximum line length
target-version = "py311"  # Python version to target

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]  # Which rules to enable
ignore = ["E501"]      # Which rules to ignore
```

**What this does:**
- `line-length`: Maximum characters per line (100 is a good balance)
- `target-version`: Python version for compatibility checks
- `select`: Enable specific rule categories (E=errors, F=pyflakes, I=isort, N=naming, W=warnings)
- `ignore`: Disable specific rules (E501 = line too long, since we set line-length)

**Complete pyproject.toml:**

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

[tool.hatch.build.targets.wheel]
packages = ["src/notes_app"]

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

🎓 **You learned**:
- How to structure a Python project with pyproject.toml
- What each dependency does and why we need it
- How to configure testing and linting tools
- How to fix the "Unable to determine which files to ship" error

### 2.8 Create the Justfile - Step by Step

The `justfile` contains shortcuts for common development tasks. Let's build it gradually:

**Step 1: Basic Setup Commands**

Create `justfile` with initialization commands:

```just
# Default Python version
python := "python3.11"

# Initialize the project
# This creates a virtual environment for Python dependencies
init:
    @echo "📦 Initializing project..."
    uv venv
    @echo "✅ Virtual environment created"
    @echo "Run: source .venv/bin/activate"

# Install dependencies
# This installs all packages defined in pyproject.toml, including dev dependencies
install:
    @echo "📦 Installing dependencies..."
    uv sync --all-extras
```

**What these do:**
- `init`: Creates a Python virtual environment using `uv`
- `install`: Installs project dependencies from `pyproject.toml`

**Step 2: Add Development Server Commands**

```just
# Start development server
# This runs uvicorn with auto-reload enabled
dev:
    @echo "🚀 Starting development server..."
    uv run uvicorn src.notes_app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
# This runs pytest on the tests directory
test:
    @echo "🧪 Running tests..."
    uv run pytest tests/ -v
```

**What these do:**
- `dev`: Starts FastAPI server with auto-reload (restarts on code changes)
- `test`: Runs all tests with verbose output

**Step 3: Add MCP Inspector Command**

```just
# Run MCP Inspector
# This opens a web interface to test your MCP server
inspect:
    @echo "🔍 Starting MCP Inspector..."
    @echo "Make sure the server is running on port 8000"
    npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

**What this does:**
- `inspect`: Launches MCP Inspector to test tools and widgets
- Requires the server to be running first

**Step 4: Add Ngrok Tunnel**

```just
# Start ngrok tunnel
# This exposes your local server to the internet (needed for ChatGPT)
tunnel:
    @echo "🌐 Starting ngrok tunnel..."
    ngrok http 8000
```

**What this does:**
- `tunnel`: Creates a public HTTPS URL pointing to localhost:8000
- Needed to connect your server to ChatGPT

**Step 5: Add Code Quality Commands**

```just
# Format code
# This formats Python code according to PEP 8
format:
    @echo "✨ Formatting code..."
    uv run ruff format .

# Lint code
# This checks for code quality issues
lint:
    @echo "🔍 Linting code..."
    uv run ruff check .
```

**What these do:**
- `format`: Auto-formats Python code
- `lint`: Checks for code style and quality issues

**Step 6: Add Utility Commands**

```just
# Clean generated files
# This removes temporary files and caches
clean:
    @echo "🧹 Cleaning generated files..."
    rm -rf .venv __pycache__ .pytest_cache .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Show environment info
# This displays information about your development environment
info:
    @echo "📊 Environment Information"
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "Python: $(which python)"
    @echo "Python version: $(python --version)"
    @echo "uv version: $(uv --version)"
    @echo "Working directory: $(pwd)"
```

**What these do:**
- `clean`: Removes temporary files and build artifacts
- `info`: Shows your current development environment details

**Complete justfile:**

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
    uv sync --all-extras

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

🎓 **You learned**:
- How to create a justfile for task automation
- What each command does and when to use it
- How to structure commands with explanations

### 2.9 Testing the Justfile Commands

Let's verify that all justfile commands work correctly.

⚠️ **Important**: At this point in the tutorial, **only `just info` will work**. The other commands require source code files that we'll create in Part 3.

**Test the info command** (works now):
```bash
just info
```

Expected output:
```
📊 Environment Information
━━━━━━━━━━━━━━━━━━━━━━━━
Python: /nix/store/.../bin/python
Python version: Python 3.11.x
uv version: uv x.x.x
Working directory: /path/to/my-notes-app
```

✅ **Checkpoint**: If `just info` works, you're ready to continue!

**Commands you'll use later in the tutorial:**

| Command | When Available | Purpose |
|---------|---------------|---------|
| `just init` | **Part 3, Section 3.2** | Creates Python virtual environment |
| `just install` | **Part 3, Section 3.2** | Installs all packages (including dev dependencies) |
| `just test` | **After install** | Runs pytest tests (once tests exist) |
| `just dev` | **After creating main.py** | Starts FastAPI server on http://localhost:8000 |
| `just inspect` | **After dev server running** | Opens MCP Inspector to test tools |
| `just tunnel` | **Part 6** | Exposes server to internet for ChatGPT |
| `just format` | **Anytime after install** | Auto-formats Python files |
| `just lint` | **Anytime after install** | Checks code quality |
| `just clean` | **Anytime** | Removes temporary files |

**Command details:**

- **`just init`** - Run once at the start of Part 3
- **`just install`** - Installs all dependencies including dev tools (pytest, ruff, etc.)
- **`just dev`** - Won't work until you create `src/notes_app/main.py` (Part 3, Section 3.5+)
- **`just test`** - Works after install, but no tests exist until later
- **`just inspect`** - Requires `just dev` running in another terminal first
- **`just tunnel`** - Use when ready to connect to ChatGPT (Part 6)

✅ **For now**: Just verify that `just info` works. You'll use the other commands as you progress through Part 3.

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

### 3.2 Install Dependencies

Now let's set up the Python environment and install dependencies.

**Step 1: Initialize the virtual environment**

```bash
just init
```

This creates a Python virtual environment in the `.venv` directory. You should see:
```
📦 Initializing project...
✅ Virtual environment created
Run: source .venv/bin/activate
```

**Step 2: Activate the virtual environment**

```bash
source .venv/bin/activate
```

Your terminal prompt should now show `(.venv)` at the beginning, indicating the virtual environment is active.

**Step 3: Install all dependencies**

```bash
just install
```

This installs all packages defined in `pyproject.toml`, including both main dependencies and dev dependencies (pytest, ruff, etc.). You should see output like:
```
📦 Installing dependencies...
Resolved XX packages in XXms
Downloaded XX packages in XXs
Installed XX packages in XXms
```

✅ **Checkpoint**: You should see all dependencies installed without errors. If you see an error about "Unable to determine which files to ship", make sure your `pyproject.toml` includes the `[tool.hatch.build.targets.wheel]` section with `packages = ["src/notes_app"]`.

You can verify the installation by checking that pytest and ruff are available:
```bash
uv run pytest --version
uv run ruff --version
```

🎓 **You learned**:
- How to initialize a Python virtual environment
- How to install dependencies using uv
- How to verify successful installation

### 3.3 Create Data Models - Step by Step

Data models define the structure of your data. Let's build `src/notes_app/models.py` gradually:

**Step 1: Basic Imports and Note Model**

Create `src/notes_app/models.py`:

```python
"""Data models for the Notes application"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Note(BaseModel):
    """A single note with title, content, and metadata

    This is the main model that represents a note in our system.
    It includes automatic timestamps for creation and updates.
    """

    # Pydantic v2 configuration
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

    # Fields
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
```

**What each part does:**
- **BaseModel**: Pydantic base class for data validation
- **model_config**: Configuration for the model (includes example for documentation)
- **Field(...)**: The `...` means the field is required
- **Field(..., min_length=1)**: Validates that title is not empty
- **default_factory**: Function called to generate default value
- **datetime.utcnow**: Automatically sets current time when note is created

**Step 2: Add Request Models**

Now add models for creating and updating notes:

```python
class NoteCreate(BaseModel):
    """Request model for creating a new note

    This model only includes the fields that the user needs to provide
    when creating a note. The ID and timestamps are generated automatically.
    """

    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., description="Note content")


class NoteUpdate(BaseModel):
    """Request model for updating an existing note

    All fields are optional so the user can update just the title,
    just the content, or both.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Note title")
    content: Optional[str] = Field(None, description="Note content")
```

**What each model does:**
- **NoteCreate**: Used when creating a new note (doesn't include ID or timestamps)
- **NoteUpdate**: Used when updating a note (all fields optional)
- **Optional[str]**: Field can be None or a string
- **Field(None, ...)**: Field is optional (None is the default)

**Step 3: Add Statistics Model**

Add a model for note statistics:

```python
class NoteStats(BaseModel):
    """Statistics about notes

    This model is used to return aggregate information
    about all notes in the system.
    """

    total: int = Field(..., description="Total number of notes")
    created_today: int = Field(0, description="Notes created today")
    updated_today: int = Field(0, description="Notes updated today")
```

**What this does:**
- **NoteStats**: Holds statistics like total count and daily activity
- **Field(0, ...)**: Field has a default value of 0

**Complete models.py:**

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

🎓 **You learned**:
- How to use Pydantic v2 to define type-safe data models
- The difference between full models and request models
- How to use Field for validation and documentation
- How to use Optional for nullable fields

### 3.4 Create Storage Layer - Step by Step

The storage layer handles data persistence. We'll use in-memory storage for simplicity. Create `src/notes_app/storage.py`:

**Step 1: Basic Storage Class**

```python
"""In-memory storage for notes with CRUD operations"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from .models import Note, NoteCreate, NoteUpdate, NoteStats


class NotesStorage:
    """Simple in-memory storage for notes

    In production, replace this with a database like PostgreSQL or SQLite.
    All data is stored in memory and will be lost when the server restarts.
    """

    def __init__(self):
        """Initialize storage with an empty dictionary"""
        self._notes: Dict[str, Note] = {}  # Dictionary mapping note ID to Note object
```

**What this does:**
- `_notes`: Private dictionary that stores notes (key=ID, value=Note object)
- `__init__`: Constructor that initializes empty storage

**Step 2: Add Create Method**

```python
    def create(self, note_create: NoteCreate) -> Note:
        """Create a new note

        Args:
            note_create: The note data to create

        Returns:
            The created Note with ID and timestamps
        """
        # Generate a new UUID for the note
        note = Note(
            id=str(uuid4()),  # Convert UUID to string
            title=note_create.title,
            content=note_create.content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Store the note
        self._notes[note.id] = note
        return note
```

**What this does:**
- Generates a unique ID using UUID
- Creates a Note object with current timestamps
- Stores it in the dictionary
- Returns the created note

**Step 3: Add List Method**

```python
    def list(self) -> List[Note]:
        """List all notes, sorted by creation date (newest first)

        Returns:
            List of all notes, sorted by created_at descending
        """
        return sorted(
            self._notes.values(),  # Get all notes
            key=lambda n: n.created_at,  # Sort by creation time
            reverse=True  # Newest first
        )
```

**What this does:**
- Returns all notes from the dictionary
- Sorts by creation date (newest first)
- Lambda function extracts the created_at field for sorting

**Step 4: Add Get Method**

```python
    def get(self, note_id: str) -> Optional[Note]:
        """Get a specific note by ID

        Args:
            note_id: The ID of the note to retrieve

        Returns:
            The note if found, None otherwise
        """
        return self._notes.get(note_id)  # Returns None if not found
```

**What this does:**
- Uses dictionary `.get()` method which returns None if key doesn't exist
- Type hint `Optional[Note]` indicates it can return None

**Step 5: Add Update Method**

```python
    def update(self, note_id: str, note_update: NoteUpdate) -> Optional[Note]:
        """Update an existing note

        Only updates fields that are provided in note_update.

        Args:
            note_id: The ID of the note to update
            note_update: The fields to update

        Returns:
            The updated note if found, None otherwise
        """
        note = self._notes.get(note_id)
        if not note:
            return None

        # Update only the fields that were provided
        if note_update.title is not None:
            note.title = note_update.title
        if note_update.content is not None:
            note.content = note_update.content

        # Always update the timestamp
        note.updated_at = datetime.utcnow()
        return note
```

**What this does:**
- Gets the existing note
- Only updates fields that are not None
- Updates the `updated_at` timestamp
- Returns None if note doesn't exist

**Step 6: Add Delete Method**

```python
    def delete(self, note_id: str) -> bool:
        """Delete a note by ID

        Args:
            note_id: The ID of the note to delete

        Returns:
            True if note was deleted, False if not found
        """
        if note_id in self._notes:
            del self._notes[note_id]
            return True
        return False
```

**What this does:**
- Checks if note exists
- Deletes it from dictionary
- Returns success status

**Step 7: Add Statistics Method**

```python
    def get_stats(self) -> NoteStats:
        """Get statistics about notes

        Calculates counts for total notes and daily activity.

        Returns:
            NoteStats object with counts
        """
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)  # Midnight today

        # Count notes created today
        created_today = sum(
            1 for note in self._notes.values()
            if note.created_at >= today_start
        )

        # Count notes updated today
        updated_today = sum(
            1 for note in self._notes.values()
            if note.updated_at >= today_start
        )

        return NoteStats(
            total=len(self._notes),
            created_today=created_today,
            updated_today=updated_today
        )
```

**What this does:**
- Gets current date at midnight
- Counts notes created/updated since midnight
- Returns statistics object

**Step 8: Add Sample Data**

```python
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

    def __init__(self):
        """Initialize storage with sample data"""
        self._notes: Dict[str, Note] = {}
        self._initialize_sample_data()  # Add sample notes
```

**What this does:**
- Creates sample notes on startup
- Helps users see the app in action immediately

**Step 9: Create Global Instance**

```python
# Global singleton instance
# This single instance is shared across the entire application
storage = NotesStorage()
```

**What this does:**
- Creates a single storage instance used by the entire app
- In production, this would be a database connection pool

**Complete storage.py:**

```python
"""In-memory storage for notes with CRUD operations"""

from datetime import datetime
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

🎓 **You learned**:
- How to implement a repository pattern for data access
- CRUD operations (Create, Read, Update, Delete)
- How to use Python dictionaries for in-memory storage
- How to calculate statistics from stored data

### 3.5 Create the MCP Server - Understanding the Architecture

Before diving into code, let's understand the MCP server architecture:

```
MCP Server Components:
┌─────────────────────────────────────────┐
│           mcp_server.py                 │
├─────────────────────────────────────────┤
│                                         │
│  1. Tool Definitions                    │
│     - Input schemas (Pydantic models)   │
│     - Tool metadata (name, description) │
│                                         │
│  2. Tool Handlers                       │
│     - Process tool calls                │
│     - Return results                    │
│                                         │
│  3. Widget Generators                   │
│     - Generate HTML for widgets         │
│     - Include JavaScript for interactivity│
│                                         │
│  4. Resource Handlers                   │
│     - Serve widget HTML                 │
│     - Handle resource requests          │
│                                         │
└─────────────────────────────────────────┘
```

Let's build this step by step. Due to the complexity, we'll break it into manageable sections.

**Continued in next message due to length...**

🎓 **What you've learned so far**:
- Project structure and configuration
- Data models with Pydantic
- Storage layer with CRUD operations
- Each file explained step by step with clear comments

The tutorial continues with:
- Part 3.6: MCP Server (simplified and explained)
- Part 4: Testing with MCP Inspector
- Part 5: **Creating Interactive Widgets (EVOLUTIONARY APPROACH - simple to complex)**
- Part 6: Connecting to ChatGPT
- Part 7: Production Deployment

Would you like me to continue with the MCP server section and especially the evolutionary widget creation?
