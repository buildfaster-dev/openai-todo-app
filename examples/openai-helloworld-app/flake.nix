{
  description = "Hola Mundo App con integración MCP";

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
            allowUnfree = true;  # Para ngrok
          };
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Entorno Python
            python311
            python311Packages.pip
            python311Packages.virtualenv

            # Gestor de paquetes
            uv

            # Task runner
            just

            # Herramientas de desarrollo
            ngrok
            curl
            jq

            # Git
            git
          ];

          shellHook = ''
            echo "👋 Hola Mundo App - Entorno de Desarrollo"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Python: $(python --version)"
            echo "uv: $(uv --version)"
            echo "just: $(just --version)"
            echo "ngrok: $(ngrok --version | head -n1)"
            echo ""
            echo "Comandos disponibles:"
            echo "  just init    - Inicializar el proyecto"
            echo "  just dev     - Iniciar servidor de desarrollo"
            echo "  just tunnel  - Iniciar túnel ngrok"
            echo "  just info    - Mostrar información"
            echo ""

            # Crear .envrc para direnv si está disponible
            if command -v direnv &> /dev/null; then
              echo "use flake" > .envrc
              direnv allow
            fi
          '';
        };
      }
    );
}
