# OpenAI ToDo App

A modern ToDo application built with the OpenAI Apps SDK, featuring a Python MCP (Model Context Protocol) server and a beautiful web interface.

## Features

- ✅ **Full CRUD Operations**: Create, read, update, and delete todos
- 🎯 **Priority Levels**: Set high, medium, or low priorities
- 🏷️ **Tags**: Organize todos with custom tags
- 📊 **Statistics Dashboard**: Track your progress with real-time stats
- 🔄 **Status Management**: Track pending, in-progress, and completed todos
- 🌐 **MCP Tools**: Ready for ChatGPT integration via OpenAI Apps SDK
- 🎨 **Modern UI**: Beautiful, responsive interface

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **MCP**: Model Context Protocol for OpenAI Apps SDK
- **Package Manager**: uv (fast Python package manager)
- **Dev Environment**: Nix for reproducible development
- **Task Runner**: Just for convenient commands
- **Tunneling**: ngrok for exposing local development

## Prerequisites

- Nix (for development environment)
- Python 3.10+ (if not using Nix)
- ngrok account (optional, for public access)

## Quick Start

### Option 1: Using Nix (Recommended)

1. **Enter the Nix shell**:
   ```bash
   nix-shell
   # or with flakes
   nix develop
   ```

2. **Initialize the project**:
   ```bash
   just init
   ```

3. **Start the development server**:
   ```bash
   just dev
   ```

4. **Open your browser**:
   Visit [http://localhost:8000](http://localhost:8000)

### Option 2: Manual Setup

1. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. **Run the server**:
   ```bash
   uv run uvicorn src.todo_app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Available Commands (Just)

```bash
just install    # Install dependencies
just dev        # Start development server
just test       # Run tests
just lint       # Run linting checks
just format     # Format code
just clean      # Clean up generated files
just tunnel     # Start ngrok tunnel (requires ngrok)
just info       # Show environment information
```

## Project Structure

```
openai-todo-app/
├── src/
│   └── todo_app/
│       ├── __init__.py
│       ├── main.py          # FastAPI app & MCP server
│       ├── models.py        # Pydantic models
│       ├── storage.py       # In-memory storage
│       ├── static/          # Static files
│       └── templates/       # HTML templates
├── tests/                   # Test files
├── pyproject.toml          # Python dependencies (uv)
├── shell.nix               # Nix development shell
├── flake.nix               # Nix flakes configuration
├── justfile                # Task automation
├── ngrok.yml               # Ngrok configuration
└── README.md
```

## API Endpoints

### REST API

- `GET /` - Web UI
- `GET /api/health` - Health check
- `POST /api/todos` - Create a new todo
- `GET /api/todos` - List all todos (with optional filters)
- `GET /api/todos/{id}` - Get a specific todo
- `PATCH /api/todos/{id}` - Update a todo
- `DELETE /api/todos/{id}` - Delete a todo
- `GET /api/stats` - Get todo statistics

### MCP Tools (for ChatGPT)

- `POST /mcp/tools/create_todo` - Create todo via MCP
- `GET /mcp/tools/list_todos` - List todos via MCP
- `POST /mcp/tools/update_todo` - Update todo via MCP
- `GET /mcp/tools/get_stats` - Get stats via MCP

## Using with OpenAI Apps SDK

### 1. Expose Your Local Server

Start ngrok to expose your local server:

```bash
just tunnel
# or
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 2. Configure in OpenAI Platform

1. Go to [OpenAI Apps Platform](https://platform.openai.com/apps)
2. Create a new app
3. Add your ngrok URL as the MCP server endpoint
4. Configure the available tools from the MCP endpoints

### 3. Test in ChatGPT

Once configured, you can interact with your todo app through ChatGPT:

```
"Create a todo for 'Review code'"
"Show me all my pending todos"
"Mark todo as completed"
"Get my todo statistics"
```

## Data Models

### TodoItem

```python
{
  "id": "uuid",
  "title": "string",
  "description": "string?",
  "status": "pending" | "in_progress" | "completed",
  "priority": "low" | "medium" | "high",
  "created_at": "datetime",
  "updated_at": "datetime",
  "due_date": "datetime?",
  "tags": ["string"]
}
```

## Development

### Running Tests

```bash
just test
```

### Code Formatting

```bash
just format
```

### Linting

```bash
just lint
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Configure your settings:

- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `NGROK_AUTHTOKEN` - Your ngrok auth token
- `DEBUG` - Enable debug mode

## Ngrok Setup

1. Sign up at [ngrok.com](https://ngrok.com)
2. Get your auth token from the [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
3. Configure in `ngrok.yml` or use environment variable
4. Run `just tunnel` to start the tunnel

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Resources

- [OpenAI Apps SDK Documentation](https://developers.openai.com/apps-sdk/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Nix Documentation](https://nixos.org/manual/nix/stable/)
- [Just Documentation](https://just.systems/)

## License

MIT License - feel free to use this project for learning and development!

## Support

If you encounter any issues or have questions:

1. Check the [OpenAI Apps SDK Quickstart](https://developers.openai.com/apps-sdk/quickstart)
2. Review the MCP documentation
3. Open an issue in this repository

---

Built with ❤️ using OpenAI Apps SDK, FastAPI, and Python
