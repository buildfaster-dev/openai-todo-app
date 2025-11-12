# OpenAI ToDo App - Development Commands

# Default recipe to display help information
default:
    @just --list

# Install dependencies using uv
install:
    @echo "📦 Installing dependencies with uv..."
    uv sync

# Run the development server
dev:
    @echo "🚀 Starting development server..."
    uv run uvicorn src.todo_app.main:app --reload --host 0.0.0.0 --port 8000

# Start ngrok tunnel for local development
tunnel port="8000":
    @echo "🌐 Starting ngrok tunnel on port {{port}}..."
    ngrok http {{port}}

# Run tests
test:
    @echo "🧪 Running tests..."
    uv run pytest tests/ -v

# Run linting and formatting checks
lint:
    @echo "🔍 Running linting checks..."
    uv run ruff check src/

# Format code
format:
    @echo "✨ Formatting code..."
    uv run ruff format src/

# Clean up generated files
clean:
    @echo "🧹 Cleaning up..."
    rm -rf .venv
    rm -rf __pycache__
    rm -rf .pytest_cache
    rm -rf src/**/__pycache__
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Initialize the project (first time setup)
init:
    @echo "🎬 Initializing project..."
    uv venv
    just install
    @echo "✅ Project initialized! Run 'just dev' to start developing."

# Show current environment info
info:
    @echo "📊 Environment Information:"
    @echo "Python: $(python --version)"
    @echo "uv: $(uv --version)"
    @echo "Working directory: $(pwd)"
    @echo ""
    @echo "Installed packages:"
    @uv pip list 2>/dev/null || echo "No venv activated"
