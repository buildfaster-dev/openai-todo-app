# CLAUDE.md - AI Assistant Guide

## Project Overview

**OpenAI ToDo App** is a modern ToDo application built with the OpenAI Apps SDK, featuring a Python MCP (Model Context Protocol) server and a beautiful web interface. It serves as both a functional application and a reference implementation for building OpenAI Apps SDK integrations.

**Primary Purpose**: Demonstrate how to build production-ready MCP servers that integrate with ChatGPT through the OpenAI Apps SDK, with interactive widgets and REST APIs.

**Tech Stack**:
- Backend: FastAPI + Python 3.11
- MCP: Model Context Protocol for OpenAI Apps SDK integration
- Package Manager: uv (fast Python package manager)
- Dev Environment: Nix for reproducible development
- Task Runner: Just for convenient commands
- Tunneling: ngrok for exposing local development

## Repository Structure

```
openai-todo-app/
├── src/
│   └── todo_app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app & MCP server integration
│       ├── mcp_server.py        # MCP protocol implementation
│       ├── models.py            # Pydantic data models
│       ├── storage.py           # In-memory storage layer
│       └── ui_components.py     # UI widget helpers
├── tests/
│   ├── test_api.py              # REST API tests
│   └── test_storage.py          # Storage layer tests
├── docs/
│   ├── README.md                # Diataxis-organized documentation
│   ├── EXPLANATION.md           # Conceptual explanations
│   ├── GUIDE.md                 # How-to guides
│   └── tutorials/               # Step-by-step tutorials
├── .specify/                    # Project specifications (Specify AI)
├── pyproject.toml              # Python dependencies & project config
├── justfile                    # Task automation commands
├── flake.nix                   # Nix flakes configuration
├── shell.nix                   # Nix development shell
├── mcp-manifest.json           # MCP tools manifest
├── .env.example                # Environment variables template
├── CONTRIBUTING.md             # Contribution guidelines
├── OPENAI_APPS_SDK.md          # OpenAI Apps SDK setup guide
└── OPENAI_SETUP.md             # OpenAI configuration guide
```

## Key Components

### Core Source Files

#### `src/todo_app/main.py`
- **Purpose**: Main application entry point
- **Key Functions**:
  - Integrates MCP server with REST API routes
  - Configures CORS middleware for OpenAI Apps SDK
  - Exposes both MCP endpoints (`/mcp`) and REST endpoints (`/api/*`)
- **Important**: Uses `mcp.streamable_http_app()` to create the Starlette app

#### `src/todo_app/mcp_server.py`
- **Purpose**: MCP protocol implementation (1279 lines)
- **Key Features**:
  - Defines MCP tools (create_todo, list_todos, update_todo, delete_todo, get_todo)
  - Implements widget resources (show_todo_app, show_todo_stats)
  - Handles MCP protocol requests (CallToolRequest, ReadResourceRequest)
  - Generates interactive HTML widgets with embedded JavaScript
- **Important Constants**:
  - `MIME_TYPE = "text/html+skybridge"` for HTML widgets
  - `PUBLIC_URL` environment variable for API base URLs in widgets
- **Widget Pattern**: Each widget has identifier, title, template_uri, invoking/invoked messages

#### `src/todo_app/models.py`
- **Purpose**: Pydantic data models
- **Models**:
  - `TodoStatus`: Enum (pending, in_progress, completed)
  - `TodoPriority`: Enum (low, medium, high)
  - `TodoItem`: Main todo item model
  - `TodoCreate`: Creation request model
  - `TodoUpdate`: Update request model (all fields optional)
- **Convention**: Uses Pydantic v2 with `model_config` and `Field` descriptors

#### `src/todo_app/storage.py`
- **Purpose**: In-memory storage layer
- **Implementation**: Global singleton `storage` instance
- **Methods**:
  - `create()`, `get()`, `list()`, `update()`, `delete()`
  - `get_stats()`: Returns statistics (total, pending, in_progress, completed, high_priority)
- **Note**: Uses UUID for todo IDs, includes sample data initialization

### Configuration Files

#### `pyproject.toml`
- **Dependencies**:
  - fastapi>=0.115.0
  - uvicorn[standard]>=0.32.0
  - pydantic>=2.9.0
  - mcp[fastapi]>=0.1.0
  - python-dotenv>=1.0.0
- **Dev Dependencies**: pytest, pytest-asyncio, httpx
- **Build**: Uses hatchling

#### `justfile`
- **Available Commands**:
  - `just install`: Install dependencies with uv
  - `just dev`: Start development server (uvicorn with reload)
  - `just test`: Run pytest
  - `just lint`: Run ruff checks
  - `just format`: Format code with ruff
  - `just clean`: Clean generated files
  - `just init`: First-time project setup
  - `just tunnel`: Start ngrok tunnel
  - `just info`: Show environment information

#### Nix Configuration
- **`flake.nix`**: Nix flakes configuration for reproducible builds
- **`shell.nix`**: Development shell with Python 3.11, uv, just, ngrok
- **Note**: Includes ngrok (unfree package) with proper configuration

## Development Workflows

### Initial Setup

**Option 1: Using Nix (Recommended)**
```bash
nix-shell  # or nix develop
just init
just dev
```

**Option 2: Manual Setup**
```bash
uv venv
source .venv/bin/activate
uv sync
just dev
```

### Development Server
- Runs on: `http://localhost:8000`
- Command: `just dev` or `uv run uvicorn src.todo_app.main:app --reload --host 0.0.0.0 --port 8000`
- Auto-reload enabled for development

### Testing
- Framework: pytest with pytest-asyncio
- Command: `just test`
- Tests located in: `tests/test_api.py`, `tests/test_storage.py`
- Coverage: API endpoints and storage layer

### Code Quality
- Linting: `just lint` (uses ruff)
- Formatting: `just format` (uses ruff)
- Convention: Follow PEP 8, use type hints

### Exposing Local Server
- Tool: ngrok
- Command: `just tunnel`
- Purpose: Expose local server for OpenAI Apps SDK integration
- Configuration: `.env` file with `NGROK_AUTHTOKEN`

## Architecture & Design Patterns

### MCP Protocol Implementation

**Transport**: Streamable HTTP (not stdio or SSE)
- Endpoint: `/mcp` (handled by FastMCP)
- Protocol: JSON-RPC 2.0
- Methods: `tools/list`, `tools/call`, `resources/list`, `resources/read`

**Tools Pattern**:
1. Define tool schema in `_list_tools()` (line 882-1013 in mcp_server.py)
2. Implement handler in `_call_tool_request()` (line 1079-1273)
3. Use Pydantic models for input validation
4. Return `types.CallToolResult` with content and optional structuredContent

**Widget Pattern**:
1. Define widget metadata (identifier, title, template_uri, invoking/invoked messages)
2. Register as resource in `_list_resources()` (line 1016-1029)
3. Generate HTML in resource handler `_handle_read_resource()` (line 1048-1076)
4. Embed API calls to REST endpoints for interactivity

### Dual API Architecture

**REST API** (`/api/*`):
- Used by interactive widgets for CRUD operations
- Standard HTTP methods (GET, POST, PATCH, DELETE)
- Returns JSON responses
- Endpoints: `/api/todos`, `/api/todos/{id}`, `/api/stats`

**MCP API** (`/mcp`):
- Used by ChatGPT for tool calls
- JSON-RPC 2.0 protocol
- Returns MCP protocol responses
- Exposes tools and resources

### Data Flow

```
ChatGPT → MCP Tool Call → mcp_server.py → storage.py → Response
                              ↓
                         Widget Resource
                              ↓
                         HTML + JavaScript
                              ↓
                         REST API calls ← User interaction
```

### Storage Pattern

- **Current**: In-memory (global singleton)
- **Production**: Swap `storage.py` implementation for database (PostgreSQL recommended)
- **Interface**: Repository pattern with CRUD methods
- **Extensibility**: Easy to replace storage backend

## Important Conventions

### Code Style

1. **Type Hints**: Always use type hints for function parameters and return values
2. **Docstrings**: Module-level and function docstrings using Google style
3. **Naming**:
   - Files: `snake_case.py`
   - Classes: `PascalCase`
   - Functions/variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`

### Pydantic Models

- Use Pydantic v2 syntax
- Define `model_config` for configuration
- Use `Field()` with descriptions for schema generation
- Use enums for status/priority fields
- Use `model_dump(mode='json')` for serialization

### MCP Tools

- Tool names: `snake_case`
- Tool titles: "Title Case"
- Input schemas: JSON Schema with additionalProperties: False
- Always include annotations (destructiveHint, openWorldHint, readOnlyHint)
- Use `_meta` for OpenAI-specific metadata

### Widget Development

- MIME type: `text/html+skybridge`
- URI pattern: `ui://widget/{widget-name}.html`
- Embed styles in `<style>` tags
- Use PUBLIC_URL for API base URLs: `const API_BASE = '{PUBLIC_URL}/api';`
- Self-contained HTML (no external CSS/JS dependencies)

### Environment Variables

- Store in `.env` file (not committed)
- Template in `.env.example`
- Load with `python-dotenv`
- Key variables:
  - `PUBLIC_URL`: Public URL for ngrok/deployed app
  - `NGROK_AUTHTOKEN`: ngrok authentication token
  - `HOST`, `PORT`: Server configuration

## Testing Guidelines

### Test Structure

- **Naming**: `test_{module}.py`
- **Organization**: Mirror source structure
- **Fixtures**: Use pytest fixtures for setup/teardown
- **Async**: Use `pytest.mark.asyncio` for async tests

### Test Coverage

- **Required**:
  - All API endpoints
  - Storage CRUD operations
  - Error conditions
- **Recommended**:
  - MCP tool calls
  - Widget generation
  - Edge cases

## AI Assistant Guidelines

### When Making Changes

1. **Read First**: Always read files before editing
2. **Understand Context**: Review related files (models, storage, tests)
3. **Follow Patterns**: Match existing code style and architecture
4. **Test**: Run tests after changes
5. **Documentation**: Update docstrings and comments

### Common Tasks

#### Adding a New MCP Tool

1. Define input schema class in `mcp_server.py` (using Pydantic)
2. Add tool definition in `_list_tools()`
3. Implement handler in `_call_tool_request()`
4. Add storage method if needed in `storage.py`
5. Write tests in `tests/test_api.py`

#### Adding a Widget

1. Define widget metadata in `widgets` list (mcp_server.py)
2. Add resource in `_list_resources()`
3. Implement HTML generator function (e.g., `_get_widget_html()`)
4. Handle in `_handle_read_resource()`
5. Create REST endpoints for widget interactivity in `main.py`

#### Modifying Data Models

1. Update model in `models.py`
2. Update storage methods in `storage.py`
3. Update MCP tool schemas in `mcp_server.py`
4. Update REST API endpoints in `main.py`
5. Update tests
6. Check widget HTML for data structure changes

### File Editing Patterns

**For small changes**: Use Edit tool
**For new files**: Use Write tool
**For reading**: Use Read tool (always read before editing)

### Git Workflow

**Branch naming**: `claude/{description}-{session-id}`
**Commit messages**: Follow Conventional Commits
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

### Dependencies

**Installing new packages**:
1. Add to `pyproject.toml` dependencies
2. Run `just install` or `uv sync`
3. Document in CLAUDE.md if significant

## Key Technologies

### FastAPI

- Modern async web framework
- Automatic OpenAPI documentation at `/docs`
- Type-safe request/response handling
- Middleware support (CORS)

### MCP (Model Context Protocol)

- Official Python SDK: `mcp[fastapi]`
- FastMCP class for server creation
- Stateless HTTP transport mode
- JSON-RPC 2.0 protocol

### uv

- Fast Python package manager (Rust-based)
- Alternative to pip
- Commands: `uv sync`, `uv run`, `uv venv`
- Lockfile: `uv.lock`

### Pydantic

- Data validation using Python type hints
- Version 2 (breaking changes from v1)
- Used for: models, request validation, OpenAPI schema

### Just

- Modern command runner (alternative to Make)
- File: `justfile`
- Syntax: Simple recipe-based
- Usage: `just <command>`

### Nix

- Reproducible development environments
- Flakes for declarative configuration
- Shell: `nix-shell` or `nix develop`
- Packages: Python, uv, just, ngrok

## Documentation

### Diataxis Framework

The `docs/` folder follows the Diataxis documentation framework:

1. **EXPLANATION.md**: Understanding (concepts, architecture, why)
2. **GUIDE.md**: How-to guides (specific tasks, troubleshooting)
3. **tutorials/**: Step-by-step learning
4. **Reference**: (in code docstrings and README)

### Key Documentation Files

- `README.md`: Quick start and overview
- `CONTRIBUTING.md`: Contribution guidelines
- `OPENAI_APPS_SDK.md`: OpenAI Apps SDK setup
- `OPENAI_SETUP.md`: OpenAI platform configuration
- `docs/GUIDE.md`: Comprehensive how-to guides
- `docs/EXPLANATION.md`: Deep conceptual explanations

### When to Update Documentation

- **README.md**: When changing setup process or adding major features
- **GUIDE.md**: When adding new how-to scenarios
- **Docstrings**: When adding/modifying functions
- **CLAUDE.md**: When changing architecture or conventions

## Common Pitfalls

### 1. PUBLIC_URL Configuration

**Problem**: Widgets fail to call API when deployed
**Solution**: Set `PUBLIC_URL` environment variable to deployed URL (not localhost)
**Where**: Used in widget HTML for API_BASE constant

### 2. CORS Issues

**Problem**: Widget API calls blocked by CORS
**Solution**: CORS middleware already configured in `main.py` with `allow_origins=["*"]`
**Note**: For production, restrict origins

### 3. Pydantic v2 Syntax

**Problem**: Using old v1 syntax
**Solution**: Use `model_config`, `model_dump()`, `model_validate()` (not `Config`, `dict()`, `parse_obj()`)

### 4. MCP Tool Schema Validation

**Problem**: Tool calls fail validation
**Solution**: Set `additionalProperties: False` in inputSchema, use Pydantic models with `extra="forbid"`

### 5. Async/Await

**Problem**: Forgetting async/await in async functions
**Solution**: All MCP handlers and FastAPI routes should use async/await properly

### 6. Storage Limitations

**Problem**: In-memory storage lost on restart
**Solution**: For production, implement persistent storage (see docs/GUIDE.md)

## Environment Setup Checklist

- [ ] Python 3.11+ installed (or use Nix)
- [ ] uv installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [ ] just installed (or use Nix)
- [ ] ngrok account created (optional, for OpenAI integration)
- [ ] `.env` file created from `.env.example`
- [ ] Virtual environment created: `uv venv`
- [ ] Dependencies installed: `just install`
- [ ] Tests passing: `just test`
- [ ] Dev server running: `just dev`

## Quick Reference

### File Locations

- **MCP Tools**: `src/todo_app/mcp_server.py` lines 882-1273
- **REST API**: `src/todo_app/main.py` lines 17-85
- **Models**: `src/todo_app/models.py`
- **Storage**: `src/todo_app/storage.py`
- **Tests**: `tests/test_api.py`, `tests/test_storage.py`
- **Config**: `pyproject.toml`, `justfile`

### Key URLs (Local Dev)

- Application: `http://localhost:8000`
- MCP Endpoint: `http://localhost:8000/mcp`
- REST API: `http://localhost:8000/api/*`
- OpenAPI Docs: `http://localhost:8000/docs`

### Important Line Numbers

- Widget definitions: `mcp_server.py:47-64`
- Tool list handler: `mcp_server.py:882-1013`
- Tool call handler: `mcp_server.py:1079-1273`
- Resource read handler: `mcp_server.py:1048-1076`
- Widget HTML generators: `mcp_server.py:134-877`

## Version Information

- **Python**: 3.11+ (specified in `.python-version`)
- **FastAPI**: 0.115.0+
- **Pydantic**: 2.9.0+
- **MCP**: 0.1.0+
- **uv**: Latest
- **pytest**: 8.3.0+

## Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [OpenAI Apps SDK Docs](https://developers.openai.com/apps-sdk/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [uv Documentation](https://docs.astral.sh/uv/)

---

**Last Updated**: 2025-11-14
**Maintained For**: Claude Code and AI assistants working with this codebase

This document should be updated when:
- Major architectural changes occur
- New patterns or conventions are established
- Key dependencies are updated
- Development workflow changes
