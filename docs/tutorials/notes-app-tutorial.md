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
mkdir openai-notes-app
cd openai-notes-app

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
# This creates a virtual environment and installs all dependencies
init:
    @echo "📦 Initializing project..."
    uv venv
    @echo "✅ Virtual environment created"
    @echo "📦 Installing dependencies..."
    uv sync --all-extras

# Install dependencies (same as init but without creating venv)
# This installs all packages defined in pyproject.toml, including dev dependencies
install:
    @echo "📦 Installing dependencies..."
    uv sync --all-extras
```

**What these do:**
- `init`: Creates a Python virtual environment using `uv` and installs all dependencies
- `install`: Installs or updates project dependencies from `pyproject.toml`

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
    @echo "📦 Installing dependencies..."
    uv sync --all-extras

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

### 2.9 Create a Minimal main.py

Before we can test the development server, we need a minimal `main.py` file. Don't worry about understanding all the details yet - we'll expand this file with full MCP functionality in Part 3.

**Why we're doing this now**: This allows us to test that our development environment is working correctly before diving into the MCP implementation.

Create the file structure:

```bash
# Create the source directory if it doesn't exist
mkdir -p src/notes_app

# Create the main.py file
touch src/notes_app/main.py
```

Now add this minimal FastAPI application to `src/notes_app/main.py`:

```python
"""Minimal FastAPI application for testing the development environment.

This is a starter file that we'll expand with MCP functionality in Part 3.
"""

from fastapi import FastAPI

# Create FastAPI application
app = FastAPI(
    title="Notes App",
    description="A notes application with MCP integration",
    version="0.1.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Notes App is running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}
```

**What this does:**
- **FastAPI app**: Creates a basic web application
- **root endpoint (`/`)**: Returns a welcome message
- **health endpoint (`/health`)**: Simple health check for monitoring
- **This is temporary**: We'll add MCP functionality in Part 3

✅ **Checkpoint**: The file should be created at `src/notes_app/main.py`

🎓 **You learned**:
- How to create a minimal FastAPI application
- Basic FastAPI endpoint structure
- The importance of health check endpoints

### 2.10 Testing the Development Environment

Now let's verify that our development environment is working correctly. We'll test several commands to ensure everything is set up properly.

**Step 1: Test the info command**

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
Working directory: /path/to/openai-notes-app
```

✅ **Checkpoint**: You should see your environment information.

**Step 2: Initialize and install dependencies**

```bash
# Create virtual environment and install dependencies
just init
```

Expected output from `just init`:
```
📦 Initializing project...
✅ Virtual environment created
📦 Installing dependencies...
Resolved XX packages in XXms
Installed XX packages in XXms
```

✅ **Checkpoint**: Virtual environment created and all dependencies should install without errors.

**Step 3: Start the development server**

```bash
just dev
```

Expected output:
```
🚀 Starting development server...
INFO:     Will watch for changes in these directories: ['/path/to/openai-notes-app']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using WatchFiles
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Checkpoint**: The server should start without errors!

**Step 4: Test the server in your browser**

Open your browser and visit:
- http://localhost:8000 - You should see: `{"status": "ok", "message": "Notes App is running", "version": "0.1.0"}`
- http://localhost:8000/health - You should see: `{"status": "healthy"}`
- http://localhost:8000/docs - You should see the FastAPI automatic documentation

**Step 5: Stop the server**

Press `Ctrl+C` in the terminal where the server is running.

**Command Availability Summary:**

| Command | Status | Purpose |
|---------|--------|---------|
| `just info` | ✅ Works now | Shows environment information |
| `just init` | ✅ Works now | Creates virtual environment and installs all dependencies |
| `just install` | ✅ Works now | Installs/updates packages (including dev dependencies) |
| `just dev` | ✅ Works now | Starts FastAPI server on http://localhost:8000 |
| `just test` | ⏳ Works but no tests yet | Runs pytest tests |
| `just format` | ✅ Works now | Auto-formats Python files |
| `just lint` | ✅ Works now | Checks code quality |
| `just clean` | ✅ Works now | Removes temporary files |
| `just inspect` | ⏳ Part 3 (after MCP server) | Opens MCP Inspector to test tools |
| `just tunnel` | ⏳ Part 6 | Exposes server to internet for ChatGPT |

**What's Next:**

In Part 3, we'll expand `main.py` to include:
- MCP server integration
- Data models for notes
- Storage layer
- MCP tools (create_note, list_notes, etc.)
- Interactive widgets

✅ **For now**: You have a working development environment with a running FastAPI server!

---

## Part 3: Building the MCP Server

Now that we have a working development environment with a minimal FastAPI server, let's build the complete MCP (Model Context Protocol) server with notes functionality.

**What we'll build in Part 3:**
1. Data models (Note, NoteCreate, NoteUpdate, NoteStats)
2. Storage layer (in-memory database)
3. Expand main.py with MCP server integration
4. MCP tools (create_note, list_notes, update_note, delete_note)
5. REST API endpoints

### 3.1 Verify Your Setup

Before we begin, make sure you completed Part 2 and have:

✅ Virtual environment activated (you should see `(.venv)` in your terminal)
✅ Dependencies installed (ran `just install`)
✅ Development server working (tested `just dev`)

If you haven't done these steps, go back to **Part 2, Section 2.10** and complete them.

**Quick verification:**

```bash
# Check that you're in the virtual environment
which python
# Should show: /path/to/openai-notes-app/.venv/bin/python

# Check that dependencies are installed
uv run pytest --version
uv run ruff --version
```

If all checks pass, you're ready to continue! 🚀

### 3.2 Create Data Models - Step by Step

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

### 3.3 Create Storage Layer - Step by Step

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

### 3.4 Expand main.py with MCP Server

Now we'll transform our minimal `main.py` into a complete MCP server. Remember, we already created a basic version in Part 2 - now we're going to expand it with full MCP functionality.

**Before diving into code**, let's understand the MCP server architecture:

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

**Step 1: Create mcp_server.py file**

First, create the MCP server module that will define all tools and resources. Create `src/notes_app/mcp_server.py`:

```python
"""MCP server implementation for Notes App"""

from mcp import FastMCP
from pydantic import BaseModel, Field

from .models import NoteCreate, NoteUpdate
from .storage import storage

# Create MCP server instance
mcp = FastMCP("Notes App")


# ============================================================================
# Tool Input Schemas (Pydantic Models)
# ============================================================================

class CreateNoteInput(BaseModel):
    """Input schema for create_note tool"""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., description="Note content")


class UpdateNoteInput(BaseModel):
    """Input schema for update_note tool"""
    note_id: str = Field(..., description="ID of the note to update")
    title: str | None = Field(None, min_length=1, max_length=200, description="New title")
    content: str | None = Field(None, description="New content")


class DeleteNoteInput(BaseModel):
    """Input schema for delete_note tool"""
    note_id: str = Field(..., description="ID of the note to delete")


class GetNoteInput(BaseModel):
    """Input schema for get_note tool"""
    note_id: str = Field(..., description="ID of the note to retrieve")


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool()
def create_note(input: CreateNoteInput) -> dict:
    """Create a new note

    Args:
        input: CreateNoteInput with title and content

    Returns:
        dict with success message and note data
    """
    note = storage.create(NoteCreate(
        title=input.title,
        content=input.content
    ))

    return {
        "success": True,
        "message": f"✅ Note '{note.title}' created successfully",
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    }


@mcp.tool()
def list_notes() -> dict:
    """List all notes

    Returns:
        dict with list of all notes
    """
    notes = storage.list()

    return {
        "success": True,
        "count": len(notes),
        "notes": [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat()
            }
            for note in notes
        ]
    }


@mcp.tool()
def get_note(input: GetNoteInput) -> dict:
    """Get a specific note by ID

    Args:
        input: GetNoteInput with note_id

    Returns:
        dict with note data or error message
    """
    note = storage.get(input.note_id)

    if not note:
        return {
            "success": False,
            "error": f"Note with ID {input.note_id} not found"
        }

    return {
        "success": True,
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    }


@mcp.tool()
def update_note(input: UpdateNoteInput) -> dict:
    """Update an existing note

    Args:
        input: UpdateNoteInput with note_id and fields to update

    Returns:
        dict with success message and updated note data
    """
    note = storage.update(
        input.note_id,
        NoteUpdate(title=input.title, content=input.content)
    )

    if not note:
        return {
            "success": False,
            "error": f"Note with ID {input.note_id} not found"
        }

    return {
        "success": True,
        "message": f"✅ Note '{note.title}' updated successfully",
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    }


@mcp.tool()
def delete_note(input: DeleteNoteInput) -> dict:
    """Delete a note by ID

    Args:
        input: DeleteNoteInput with note_id

    Returns:
        dict with success message or error
    """
    success = storage.delete(input.note_id)

    if not success:
        return {
            "success": False,
            "error": f"Note with ID {input.note_id} not found"
        }

    return {
        "success": True,
        "message": f"✅ Note deleted successfully"
    }


@mcp.tool()
def get_notes_stats() -> dict:
    """Get statistics about notes

    Returns:
        dict with note statistics
    """
    stats = storage.get_stats()

    return {
        "success": True,
        "stats": {
            "total": stats.total,
            "created_today": stats.created_today,
            "updated_today": stats.updated_today
        }
    }
```

**What this file does:**
- **FastMCP**: Creates an MCP server instance
- **Input schemas**: Pydantic models for validating tool inputs
- **@mcp.tool()**: Decorator that registers functions as MCP tools
- **Each tool**: Returns a dictionary with success status and data
- **Error handling**: Returns error messages when operations fail

**Step 2: Update main.py to integrate MCP server**

Now update `src/notes_app/main.py` to integrate the MCP server with FastAPI:

```python
"""Main FastAPI application with MCP integration"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .mcp_server import mcp
from .models import NoteCreate, NoteUpdate
from .storage import storage

# Get public URL from environment (needed for widgets)
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")

# Create FastAPI app
app = FastAPI(
    title="Notes App",
    description="A notes application with MCP integration for ChatGPT",
    version="0.1.0"
)

# Enable CORS for OpenAI Apps SDK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP server at /mcp endpoint
app.mount("/mcp", mcp.streamable_http_app())


# ============================================================================
# REST API Endpoints (used by widgets and direct API access)
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Notes App is running",
        "version": "0.1.0",
        "mcp_endpoint": "/mcp"
    }


@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


@app.get("/api/notes")
async def api_list_notes():
    """List all notes"""
    notes = storage.list()
    return {
        "notes": [note.model_dump(mode="json") for note in notes]
    }


@app.post("/api/notes")
async def api_create_note(note_create: NoteCreate):
    """Create a new note"""
    note = storage.create(note_create)
    return note.model_dump(mode="json")


@app.get("/api/notes/{note_id}")
async def api_get_note(note_id: str):
    """Get a specific note"""
    note = storage.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note.model_dump(mode="json")


@app.patch("/api/notes/{note_id}")
async def api_update_note(note_id: str, note_update: NoteUpdate):
    """Update a note"""
    note = storage.update(note_id, note_update)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note.model_dump(mode="json")


@app.delete("/api/notes/{note_id}")
async def api_delete_note(note_id: str):
    """Delete a note"""
    success = storage.delete(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"success": True}


@app.get("/api/stats")
async def api_get_stats():
    """Get note statistics"""
    stats = storage.get_stats()
    return stats.model_dump(mode="json")
```

**What this does:**
- **app.mount("/mcp", ...)**: Mounts the MCP server at `/mcp` endpoint
- **CORS middleware**: Allows ChatGPT to call your API
- **REST endpoints**: Provide API access for widgets and direct use
- **Error handling**: Returns 404 when notes not found

✅ **Checkpoint**: Your MCP server is now integrated with FastAPI!

**Step 3: Create __init__.py**

Create `src/notes_app/__init__.py` to make it a proper Python package:

```python
"""Notes App - MCP integration for ChatGPT"""

__version__ = "0.1.0"
```

**Step 4: Test the server**

```bash
# Start the development server
just dev
```

Visit these URLs in your browser:
- http://localhost:8000 - Should show API info
- http://localhost:8000/docs - Should show FastAPI documentation with all endpoints
- http://localhost:8000/mcp - Should show MCP server response

🎓 **You learned**:
- How to create MCP tools using FastMCP
- How to define input schemas with Pydantic
- How to integrate MCP server with FastAPI
- How to create both MCP tools and REST endpoints
- The dual API architecture (MCP + REST)

---

## Part 4: Testing with MCP Inspector

### 4.1 What is MCP Inspector?

**MCP Inspector** is a web-based tool for testing MCP servers. It allows you to:
- Discover available tools
- Call tools with different inputs
- View tool responses
- Test before connecting to ChatGPT

Think of it as Postman for MCP servers.

### 4.2 Start the Development Server

In one terminal:

```bash
just dev
```

Keep this running throughout testing.

### 4.3 Launch MCP Inspector

In a **second terminal** (keep the server running in the first):

```bash
# Make sure you're in the project directory
cd openai-notes-app

# Enter the Nix shell if you haven't already
nix develop

# Launch MCP Inspector
just inspect
```

Expected output:
```
🔍 Starting MCP Inspector...
Make sure the server is running on port 8000
MCP Inspector is available at http://localhost:5173
```

### 4.4 Connect to Your Server

1. **Open the URL**: Visit http://localhost:5173 in your browser
2. **Enter your server URL**: `http://localhost:8000/mcp`
3. **Click "Connect"**

You should see a list of available tools:
- `create_note`
- `list_notes`
- `get_note`
- `update_note`
- `delete_note`
- `get_notes_stats`

### 4.5 Test Each Tool

**Test 1: List Notes**

1. Click on `list_notes` tool
2. Click "Call Tool" (no parameters needed)
3. You should see the sample notes created in storage

Expected response:
```json
{
  "success": true,
  "count": 2,
  "notes": [
    {
      "id": "...",
      "title": "MCP Integration",
      "content": "This app uses the Model Context Protocol...",
      "created_at": "...",
      "updated_at": "..."
    },
    {
      "id": "...",
      "title": "Welcome to Notes App",
      "content": "This is your first note...",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

**Test 2: Create a Note**

1. Click on `create_note` tool
2. Enter parameters:
   ```json
   {
     "title": "Test Note",
     "content": "This is a test note created from MCP Inspector"
   }
   ```
3. Click "Call Tool"

Expected response:
```json
{
  "success": true,
  "message": "✅ Note 'Test Note' created successfully",
  "note": {
    "id": "...",
    "title": "Test Note",
    "content": "This is a test note created from MCP Inspector",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

**Test 3: Get Statistics**

1. Click on `get_notes_stats` tool
2. Click "Call Tool"

Expected response:
```json
{
  "success": true,
  "stats": {
    "total": 3,
    "created_today": 3,
    "updated_today": 3
  }
}
```

**Test 4: Update a Note**

1. First, run `list_notes` and copy a note ID
2. Click on `update_note` tool
3. Enter parameters:
   ```json
   {
     "note_id": "paste-note-id-here",
     "title": "Updated Title",
     "content": "Updated content"
   }
   ```
4. Click "Call Tool"

**Test 5: Delete a Note**

1. Click on `delete_note` tool
2. Enter parameters:
   ```json
   {
     "note_id": "paste-note-id-here"
   }
   ```
3. Click "Call Tool"

Expected response:
```json
{
  "success": true,
  "message": "✅ Note deleted successfully"
}
```

### 4.6 Troubleshooting

**Problem: Can't connect to server**
- Solution: Make sure `just dev` is running in another terminal
- Check that http://localhost:8000 is accessible

**Problem: Tools not showing up**
- Solution: Check server logs for errors
- Make sure you entered the correct URL: `http://localhost:8000/mcp`

**Problem: Tool calls fail**
- Solution: Check the error message
- Verify input format matches the schema
- Check server logs for detailed errors

### 4.7 Understanding the Test Results

**What you verified:**
- ✅ MCP server is running correctly
- ✅ All tools are registered and discoverable
- ✅ Tools accept inputs and validate them
- ✅ Tools return proper responses
- ✅ Storage layer works correctly
- ✅ Error handling works (try invalid note IDs)

🎓 **You learned**:
- How to use MCP Inspector to test MCP servers
- How to call tools with different inputs
- How to verify tool responses
- How to debug MCP server issues

---

## Part 5: Creating Interactive Widgets

### 5.1 Understanding Widgets

**Widgets** are interactive HTML interfaces displayed in ChatGPT. They allow users to:
- View data in a visual format
- Interact with your app without leaving ChatGPT
- Trigger actions (like creating or deleting notes)

**Widget Architecture:**

```
┌─────────────────────────────────────┐
│         ChatGPT Window              │
├─────────────────────────────────────┤
│                                     │
│  Chat: "Show me my notes"           │
│                                     │
│  ┌───────────────────────────────┐ │
│  │    Interactive Widget         │ │
│  ├───────────────────────────────┤ │
│  │  📝 My Notes                  │ │
│  │                               │ │
│  │  • Note 1        [Edit] [Del] │ │
│  │  • Note 2        [Edit] [Del] │ │
│  │                               │ │
│  │  [+ Create Note]              │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### 5.2 How Widgets Work

**Key Concepts:**

1. **Widget Resources**: MCP resources that return HTML
2. **HTML + JavaScript**: Self-contained interactive interfaces
3. **window.openai API**: JavaScript API to call MCP tools
4. **Structured Content**: Data passed from tools to widgets

**Communication Flow:**

```
User asks ChatGPT
    ↓
ChatGPT calls MCP tool
    ↓
Tool returns data + widget reference
    ↓
ChatGPT requests widget HTML
    ↓
Widget displayed in ChatGPT
    ↓
User clicks button in widget
    ↓
JavaScript calls window.openai.callTool()
    ↓
Tool processes request
    ↓
Widget updates
```

### 5.3 Add Widget Resources to mcp_server.py

Update `src/notes_app/mcp_server.py` to add widget support. Add this at the end of the file:

```python
# ============================================================================
# Widget Resources
# ============================================================================

@mcp.resource("widget://notes-list")
def notes_list_widget() -> str:
    """Widget to display and manage notes"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}

            .container {{
                max-width: 800px;
                margin: 0 auto;
            }}

            .header {{
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }}

            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}

            .stats {{
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
                margin-bottom: 30px;
            }}

            .stat-card {{
                background: white;
                padding: 15px 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}

            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }}

            .stat-label {{
                color: #666;
                font-size: 0.9em;
            }}

            .create-section {{
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}

            .create-section h2 {{
                margin-bottom: 15px;
                color: #333;
            }}

            .form-group {{
                margin-bottom: 15px;
            }}

            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #555;
            }}

            input, textarea {{
                width: 100%;
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s;
            }}

            input:focus, textarea:focus {{
                outline: none;
                border-color: #667eea;
            }}

            textarea {{
                min-height: 100px;
                resize: vertical;
                font-family: inherit;
            }}

            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: 500;
            }}

            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}

            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}

            .btn-secondary {{
                background: #f0f0f0;
                color: #333;
                padding: 8px 16px;
                font-size: 0.9em;
            }}

            .btn-secondary:hover {{
                background: #e0e0e0;
            }}

            .btn-danger {{
                background: #ff4444;
                color: white;
                padding: 8px 16px;
                font-size: 0.9em;
            }}

            .btn-danger:hover {{
                background: #cc0000;
            }}

            .notes-list {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}

            .note-card {{
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                transition: transform 0.3s;
            }}

            .note-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            }}

            .note-header {{
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 10px;
            }}

            .note-title {{
                font-size: 1.3em;
                font-weight: bold;
                color: #333;
                flex: 1;
            }}

            .note-actions {{
                display: flex;
                gap: 8px;
            }}

            .note-content {{
                color: #666;
                line-height: 1.6;
                margin-bottom: 10px;
                white-space: pre-wrap;
            }}

            .note-meta {{
                font-size: 0.85em;
                color: #999;
            }}

            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}

            .empty-state-icon {{
                font-size: 4em;
                margin-bottom: 20px;
            }}

            .empty-state h2 {{
                color: #666;
                margin-bottom: 10px;
            }}

            .empty-state p {{
                color: #999;
            }}

            .loading {{
                text-align: center;
                padding: 40px;
                color: white;
                font-size: 1.2em;
            }}

            .error {{
                background: #ffebee;
                color: #c62828;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📝 My Notes</h1>
                <p>Manage your notes with AI assistance</p>
            </div>

            <div id="stats" class="stats"></div>

            <div class="create-section">
                <h2>✨ Create New Note</h2>
                <div class="form-group">
                    <label for="title">Title</label>
                    <input type="text" id="title" placeholder="Enter note title...">
                </div>
                <div class="form-group">
                    <label for="content">Content</label>
                    <textarea id="content" placeholder="Enter note content..."></textarea>
                </div>
                <button class="btn btn-primary" onclick="createNote()">Create Note</button>
            </div>

            <div id="notes-container" class="loading">Loading notes...</div>
        </div>

        <script>
            const API_BASE = '{PUBLIC_URL}/api';

            // Load notes on page load
            window.addEventListener('load', () => {{
                loadNotes();
                loadStats();
            }});

            async function loadNotes() {{
                try {{
                    const response = await fetch(`${{API_BASE}}/notes`);
                    const data = await response.json();
                    displayNotes(data.notes);
                }} catch (error) {{
                    document.getElementById('notes-container').innerHTML =
                        '<div class="error">Failed to load notes. Please try again.</div>';
                }}
            }}

            async function loadStats() {{
                try {{
                    const response = await fetch(`${{API_BASE}}/stats`);
                    const stats = await response.json();
                    displayStats(stats);
                }} catch (error) {{
                    console.error('Failed to load stats:', error);
                }}
            }}

            function displayStats(stats) {{
                const statsHtml = `
                    <div class="stat-card">
                        <div class="stat-number">${{stats.total}}</div>
                        <div class="stat-label">Total Notes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{stats.created_today}}</div>
                        <div class="stat-label">Created Today</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{stats.updated_today}}</div>
                        <div class="stat-label">Updated Today</div>
                    </div>
                `;
                document.getElementById('stats').innerHTML = statsHtml;
            }}

            function displayNotes(notes) {{
                const container = document.getElementById('notes-container');

                if (notes.length === 0) {{
                    container.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📭</div>
                            <h2>No notes yet</h2>
                            <p>Create your first note using the form above!</p>
                        </div>
                    `;
                    return;
                }}

                const notesHtml = notes.map(note => `
                    <div class="note-card">
                        <div class="note-header">
                            <div class="note-title">${{escapeHtml(note.title)}}</div>
                            <div class="note-actions">
                                <button class="btn btn-secondary" onclick="editNote('${{note.id}}')">
                                    ✏️ Edit
                                </button>
                                <button class="btn btn-danger" onclick="deleteNote('${{note.id}}')">
                                    🗑️ Delete
                                </button>
                            </div>
                        </div>
                        <div class="note-content">${{escapeHtml(note.content)}}</div>
                        <div class="note-meta">
                            Created: ${{new Date(note.created_at).toLocaleString()}}
                        </div>
                    </div>
                `).join('');

                container.innerHTML = `<div class="notes-list">${{notesHtml}}</div>`;
            }}

            async function createNote() {{
                const title = document.getElementById('title').value.trim();
                const content = document.getElementById('content').value.trim();

                if (!title || !content) {{
                    alert('Please fill in both title and content');
                    return;
                }}

                try {{
                    const response = await fetch(`${{API_BASE}}/notes`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ title, content }})
                    }});

                    if (response.ok) {{
                        document.getElementById('title').value = '';
                        document.getElementById('content').value = '';
                        loadNotes();
                        loadStats();
                    }} else {{
                        alert('Failed to create note');
                    }}
                }} catch (error) {{
                    alert('Error creating note: ' + error.message);
                }}
            }}

            async function deleteNote(noteId) {{
                if (!confirm('Are you sure you want to delete this note?')) {{
                    return;
                }}

                try {{
                    const response = await fetch(`${{API_BASE}}/notes/${{noteId}}`, {{
                        method: 'DELETE'
                    }});

                    if (response.ok) {{
                        loadNotes();
                        loadStats();
                    }} else {{
                        alert('Failed to delete note');
                    }}
                }} catch (error) {{
                    alert('Error deleting note: ' + error.message);
                }}
            }}

            async function editNote(noteId) {{
                const newTitle = prompt('Enter new title (or leave empty to keep current):');
                const newContent = prompt('Enter new content (or leave empty to keep current):');

                if (!newTitle && !newContent) {{
                    return;
                }}

                const updates = {{}};
                if (newTitle) updates.title = newTitle;
                if (newContent) updates.content = newContent;

                try {{
                    const response = await fetch(`${{API_BASE}}/notes/${{noteId}}`, {{
                        method: 'PATCH',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(updates)
                    }});

                    if (response.ok) {{
                        loadNotes();
                        loadStats();
                    }} else {{
                        alert('Failed to update note');
                    }}
                }} catch (error) {{
                    alert('Error updating note: ' + error.message);
                }}
            }}

            function escapeHtml(text) {{
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }}
        </script>
    </body>
    </html>
    """

    return html


# Update the list_notes tool to reference the widget
# Modify the existing list_notes function:
@mcp.tool()
def list_notes() -> dict:
    """List all notes and show interactive widget

    Returns:
        dict with list of all notes and widget reference
    """
    notes = storage.list()

    return {
        "success": True,
        "count": len(notes),
        "notes": [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat()
            }
            for note in notes
        ],
        "_meta": {
            "widget": {
                "resource_uri": "widget://notes-list",
                "title": "My Notes"
            }
        }
    }
```

**What this widget does:**
- **HTML + CSS**: Creates a beautiful, responsive interface
- **JavaScript**: Loads notes from REST API
- **Statistics**: Shows note counts
- **Create form**: Allows creating new notes
- **Note cards**: Displays each note with edit/delete buttons
- **Interactive**: Full CRUD operations without leaving ChatGPT

**Key Features:**
- Uses `PUBLIC_URL` for API calls (works in production)
- Gradient design for visual appeal
- Responsive layout
- Error handling
- Empty state when no notes exist
- Real-time updates after actions

### 5.4 Test the Widget

**Step 1: Restart the server**

Stop the server (Ctrl+C) and restart it to load the widget:

```bash
just dev
```

**Step 2: Test with MCP Inspector**

1. Make sure MCP Inspector is still running (`just inspect` in another terminal)
2. Call the `list_notes` tool
3. Look for the `_meta` field in the response - it should contain the widget reference

**Step 3: View the widget directly**

Open your browser and visit:
```
http://localhost:8000/mcp/resources/widget://notes-list
```

You should see the beautiful notes interface!

**What you can do:**
- ✅ View all notes
- ✅ See statistics (total, created today, updated today)
- ✅ Create new notes using the form
- ✅ Edit existing notes
- ✅ Delete notes
- ✅ See real-time updates

🎓 **You learned**:
- How to create interactive HTML widgets
- How to use the widget resource pattern
- How to integrate JavaScript with REST APIs
- How to pass widget references from tools
- How to build responsive, beautiful UIs

---

## Part 6: Connecting to ChatGPT

### 6.1 Prerequisites

Before connecting to ChatGPT, you need:
- ✅ Working MCP server (from Part 3)
- ✅ Tested tools (from Part 4)
- ✅ Interactive widget (from Part 5)
- ✅ ngrok account (free) - [Sign up at ngrok.com](https://ngrok.com)

### 6.2 Set Up ngrok

**Step 1: Create ngrok account**

1. Visit https://ngrok.com
2. Sign up for a free account
3. Go to "Your Authtoken" page
4. Copy your authtoken

**Step 2: Configure ngrok**

Create `.env` file in your project root:

```bash
# In the project directory (openai-notes-app/)
touch .env
```

Add your ngrok authtoken to `.env`:

```env
# ngrok configuration
NGROK_AUTHTOKEN=your_authtoken_here

# This will be set automatically by ngrok
PUBLIC_URL=
```

**Step 3: Authenticate ngrok**

```bash
ngrok config add-authtoken your_authtoken_here
```

### 6.3 Expose Your Server

**Step 1: Start your development server**

In terminal 1:

```bash
just dev
```

**Step 2: Start ngrok tunnel**

In terminal 2:

```bash
just tunnel
```

You'll see output like:
```
Session Status                online
Account                       yourname (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

**Step 3: Update .env with your public URL**

Edit `.env`:

```env
NGROK_AUTHTOKEN=your_authtoken_here
PUBLIC_URL=https://abc123.ngrok.io
```

**Step 4: Restart the server**

Stop (`Ctrl+C`) and restart `just dev` to load the new PUBLIC_URL.

### 6.4 Create OpenAI App Configuration

**Step 1: Create mcp-manifest.json**

In your project root, create `mcp-manifest.json`:

```json
{
  "version": "0.1",
  "name": "Notes App",
  "description": "Create and manage notes with AI assistance",
  "transport": {
    "type": "http",
    "url": "https://your-ngrok-url.ngrok.io/mcp"
  }
}
```

**Replace `https://your-ngrok-url.ngrok.io`** with your actual ngrok URL!

**Step 2: Verify the manifest**

Test that your MCP endpoint is publicly accessible:

```bash
curl https://your-ngrok-url.ngrok.io/mcp
```

You should get an MCP response (not an error).

### 6.5 Connect to ChatGPT

**Step 1: Open ChatGPT**

Visit https://chat.openai.com

**Step 2: Upload the manifest**

1. Click on your name (bottom left)
2. Select "Settings"
3. Go to "Apps" tab
4. Click "Connect App"
5. Upload your `mcp-manifest.json` file

**Step 3: Authorize the app**

ChatGPT will show you:
- App name: "Notes App"
- Tools that will be available
- Click "Allow"

**Step 4: Test in ChatGPT**

Try these prompts:

```
"List my notes"
```

ChatGPT should:
1. Call the `list_notes` tool
2. Display the interactive widget
3. You can interact with the widget!

```
"Create a note titled 'Meeting Notes' with content 'Discussed Q4 roadmap'"
```

ChatGPT should:
1. Call the `create_note` tool
2. Confirm creation
3. Show the updated notes list

```
"Show me statistics about my notes"
```

```
"Delete the note about meetings"
```

### 6.6 Understanding the Flow

When you ask ChatGPT to interact with notes:

```
User: "List my notes"
    ↓
ChatGPT → POST https://your-ngrok-url.ngrok.io/mcp
          (method: tools/call, name: list_notes)
    ↓
Your Server → Processes request
              Calls storage.list()
              Returns notes + widget reference
    ↓
ChatGPT → POST https://your-ngrok-url.ngrok.io/mcp
          (method: resources/read, uri: widget://notes-list)
    ↓
Your Server → Returns HTML widget
    ↓
ChatGPT → Displays widget in chat
    ↓
User clicks "Create Note" in widget
    ↓
Widget JavaScript → POST https://your-ngrok-url.ngrok.io/api/notes
                    (REST API call)
    ↓
Your Server → Creates note
              Returns new note data
    ↓
Widget updates to show new note
```

### 6.7 Troubleshooting

**Problem: ChatGPT can't connect**
- Check that ngrok tunnel is running
- Verify PUBLIC_URL in .env matches ngrok URL
- Make sure server restarted after changing .env
- Test the endpoint manually: `curl https://your-ngrok-url.ngrok.io/mcp`

**Problem: Tools work but widget doesn't show**
- Check that `_meta.widget.resource_uri` is in tool response
- Verify widget resource is registered
- Check browser console for errors

**Problem: Widget shows but can't interact**
- Verify PUBLIC_URL is set correctly
- Check CORS is enabled in main.py
- Look at browser console for API errors

**Problem: ngrok URL changes**
- Free ngrok URLs change each time you restart
- Update mcp-manifest.json with new URL
- Update PUBLIC_URL in .env
- Restart server
- Re-upload manifest to ChatGPT

🎓 **You learned**:
- How to expose local development to the internet with ngrok
- How to create OpenAI app manifests
- How to connect MCP servers to ChatGPT
- The complete request/response flow
- How to debug connection issues

---

## Part 7: Production Deployment

### 7.1 Production Considerations

For production deployment, you need to handle:
- **Persistent storage**: Replace in-memory storage with a database
- **Environment variables**: Secure configuration
- **HTTPS**: Secure communication
- **CORS**: Restrict allowed origins
- **Error handling**: Robust error responses
- **Monitoring**: Track usage and errors
- **Rate limiting**: Prevent abuse

### 7.2 Database Integration (PostgreSQL Example)

**Step 1: Update pyproject.toml**

Add database dependencies:

```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "mcp[fastapi]>=0.1.0",
    "pydantic>=2.9.0",
    "python-dotenv>=1.0.0",
    "asyncpg>=0.29.0",  # PostgreSQL driver
    "sqlalchemy[asyncio]>=2.0.0",  # ORM
]
```

**Step 2: Create database models**

Create `src/notes_app/database.py`:

```python
"""Database configuration and models"""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/notesdb")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


class NoteDB(Base):
    """Database model for notes"""
    __tablename__ = "notes"

    id = Column(String, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Step 3: Update storage.py for database**

Replace `storage.py` with database-backed version:

```python
"""Database-backed storage for notes"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Note, NoteCreate, NoteUpdate, NoteStats
from .database import async_session, NoteDB


class NotesStorage:
    """Database-backed storage for notes"""

    async def create(self, note_create: NoteCreate) -> Note:
        """Create a new note"""
        async with async_session() as session:
            db_note = NoteDB(
                id=str(uuid4()),
                title=note_create.title,
                content=note_create.content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(db_note)
            await session.commit()
            await session.refresh(db_note)

            return Note(
                id=db_note.id,
                title=db_note.title,
                content=db_note.content,
                created_at=db_note.created_at,
                updated_at=db_note.updated_at
            )

    async def list(self) -> List[Note]:
        """List all notes"""
        async with async_session() as session:
            result = await session.execute(
                select(NoteDB).order_by(NoteDB.created_at.desc())
            )
            db_notes = result.scalars().all()

            return [
                Note(
                    id=note.id,
                    title=note.title,
                    content=note.content,
                    created_at=note.created_at,
                    updated_at=note.updated_at
                )
                for note in db_notes
            ]

    # Add other methods (get, update, delete, get_stats)...


# Global singleton
storage = NotesStorage()
```

### 7.3 Deploy to Render.com (Free Tier)

**Step 1: Prepare for deployment**

Create `requirements.txt`:

```bash
# Generate from pyproject.toml
uv pip compile pyproject.toml -o requirements.txt
```

Create `render.yaml`:

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
      - key: DATABASE_URL
        fromDatabase:
          name: notesdb
          property: connectionString

databases:
  - name: notesdb
    databaseName: notesdb
    user: notesuser
```

**Step 2: Deploy**

1. Push code to GitHub
2. Go to https://render.com
3. Click "New +" → "Blueprint"
4. Connect your repository
5. Render will automatically detect `render.yaml`
6. Click "Apply"

**Step 3: Update OpenAI manifest**

Update `mcp-manifest.json` with your production URL:

```json
{
  "version": "0.1",
  "name": "Notes App",
  "description": "Create and manage notes with AI assistance",
  "transport": {
    "type": "http",
    "url": "https://your-app.onrender.com/mcp"
  }
}
```

Re-upload to ChatGPT.

### 7.4 Deploy to Vercel (Alternative)

Create `vercel.json`:

```json
{
  "builds": [
    {
      "src": "src/notes_app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "src/notes_app/main.py"
    }
  ]
}
```

Deploy:

```bash
npx vercel
```

### 7.5 Production Checklist

Before going to production:

- [ ] **Security**
  - [ ] Use environment variables for secrets
  - [ ] Restrict CORS to specific origins
  - [ ] Add rate limiting
  - [ ] Implement authentication if needed
  - [ ] Use HTTPS only

- [ ] **Database**
  - [ ] Set up production database (PostgreSQL recommended)
  - [ ] Configure connection pooling
  - [ ] Set up automated backups
  - [ ] Run migrations

- [ ] **Monitoring**
  - [ ] Set up error tracking (Sentry)
  - [ ] Configure logging
  - [ ] Add health check endpoints
  - [ ] Monitor performance

- [ ] **Configuration**
  - [ ] Set PUBLIC_URL to production domain
  - [ ] Configure proper CORS origins
  - [ ] Set up environment variables
  - [ ] Test all tools and widgets

- [ ] **Documentation**
  - [ ] Update README with deployment instructions
  - [ ] Document environment variables
  - [ ] Add troubleshooting guide
  - [ ] Write API documentation

### 7.6 Environment Variables Reference

Required environment variables for production:

```env
# Application
PUBLIC_URL=https://your-production-domain.com
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Security (if using authentication)
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://chat.openai.com

# Optional
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### 7.7 Scaling Considerations

As your app grows:

**Vertical Scaling:**
- Increase server resources (CPU, RAM)
- Use production-grade ASGI server (Gunicorn + Uvicorn workers)

**Horizontal Scaling:**
- Add load balancer
- Run multiple instances
- Use Redis for session storage
- Implement caching (Redis, Memcached)

**Database Scaling:**
- Connection pooling
- Read replicas
- Database indexes
- Query optimization

**Example production server command:**

```bash
gunicorn src.notes_app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

🎓 **You learned**:
- How to prepare an MCP app for production
- Database integration patterns
- Deployment to cloud platforms
- Production security best practices
- Scaling strategies
- Monitoring and observability

---

## Conclusion

### What You Built

Congratulations! 🎉 You've built a complete production-ready MCP application:

- ✅ **Nix development environment** - Reproducible setup
- ✅ **FastAPI backend** - Modern async web framework
- ✅ **MCP server** - 7 tools for note management
- ✅ **Interactive widget** - Beautiful HTML interface
- ✅ **REST API** - For widget interactions
- ✅ **ChatGPT integration** - Full AI assistant integration
- ✅ **Production deployment** - Ready to scale

### Key Skills You Learned

1. **MCP Protocol**
   - Understanding JSON-RPC 2.0
   - Defining tools with input schemas
   - Creating widget resources
   - Structured content passing

2. **Python Development**
   - Pydantic for data validation
   - FastAPI for web APIs
   - Async programming
   - Type hints and validation

3. **Frontend Development**
   - HTML/CSS for beautiful UIs
   - JavaScript for interactivity
   - REST API integration
   - Responsive design

4. **DevOps**
   - Nix for reproducible environments
   - Just for task automation
   - ngrok for local tunneling
   - Production deployment

5. **AI Integration**
   - ChatGPT Apps SDK
   - Widget-based UIs
   - Tool calling patterns
   - Testing with MCP Inspector

### Next Steps

**Enhance the app:**
- Add categories/tags to notes
- Implement search functionality
- Add markdown rendering
- Support file attachments
- Add sharing capabilities

**Learn more:**
- Explore other MCP transports (SSE, stdio)
- Build more complex widgets
- Integrate with other AI models
- Create multi-step workflows

**Build something new:**
- Task management app
- Knowledge base
- CRM system
- Project tracker
- Team collaboration tool

### Resources

- **MCP Specification**: https://modelcontextprotocol.io/
- **OpenAI Apps SDK**: https://developers.openai.com/apps-sdk/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **This project**: Check out the OpenAI ToDo App for more examples

### Thank You!

You've completed the comprehensive MCP tutorial! You now have the knowledge to build production-ready AI-integrated applications.

**Questions or Issues?**
- Check the troubleshooting sections
- Review the OpenAI ToDo App codebase
- Join the MCP community
- Experiment and build!

Happy coding! 🚀
