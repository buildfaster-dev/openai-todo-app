{
  description = "OpenAI ToDo App Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
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
        };
      }
    );
}
