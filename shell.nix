{ pkgs ? import <nixpkgs> { config.allowUnfree = true; } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python and uv package manager
    python311
    uv

    # Development tools
    just
    ngrok

    # Additional utilities
    git
    curl
  ];

  shellHook = ''
    echo "🚀 OpenAI ToDo App Development Environment"
    echo "=========================================="
    echo "Python:  $(python --version)"
    echo "uv:      $(uv --version)"
    echo "just:    $(just --version)"
    echo "ngrok:   $(ngrok version)"
    echo ""
    echo "Quick start:"
    echo "  just install  - Install dependencies"
    echo "  just dev      - Start development server"
    echo "  just tunnel   - Start ngrok tunnel"
    echo ""

    # Set up UV to use project-local virtual environment
    export UV_PROJECT_ENVIRONMENT=".venv"
  '';
}
