# Tutorial: Hola Mundo con OpenAI Apps SDK

> **Tipo de Documento**: Tutorial (Orientado al aprendizaje)
> **Objetivo**: Entender los conceptos básicos de MCP y crear tu primera aplicación
> **Tiempo Estimado**: 30-45 minutos
> **Nivel**: Principiante absoluto

## Objetivos de Aprendizaje

Al final de este tutorial, entenderás:

1. **Qué es el Model Context Protocol (MCP)** - El estándar de comunicación entre asistentes de IA y herramientas externas
2. **Cómo se comunican los servidores MCP con ChatGPT** - Protocolo JSON-RPC, herramientas y recursos
3. **Cómo crear y registrar herramientas** - Definir funciones que ChatGPT puede llamar
4. **Cómo crear widgets HTML para ChatGPT** - Construir interfaces visuales interactivas
5. **Cómo usar la API `window.openai`** - Permitir que widgets llamen herramientas desde JavaScript
6. **Cómo conectar tu servidor a ChatGPT** - Integración con OpenAI Apps SDK

## Introducción

En este tutorial, construirás una **Aplicación Hola Mundo** que se integra con ChatGPT usando el Model Context Protocol (MCP). Empezarás desde cero, creando un entorno de desarrollo con Nix, implementando una herramienta MCP simple, y construyendo un widget interactivo.

**Lo que construirás**: Una aplicación simple que saluda a las personas, con un widget interactivo que se muestra directamente en la interfaz de ChatGPT.

## Tabla de Contenidos

- [Parte 1: Entendiendo MCP](#parte-1-entendiendo-mcp)
- [Parte 2: Configuración con Nix](#parte-2-configuración-con-nix)
- [Parte 3: Construyendo el Servidor MCP](#parte-3-construyendo-el-servidor-mcp)
- [Parte 4: Probando Localmente](#parte-4-probando-localmente)
- [Parte 5: Conectando con ChatGPT](#parte-5-conectando-con-chatgpt)

---

## Parte 1: Entendiendo MCP

### 1.1 ¿Qué es el Model Context Protocol?

El **Model Context Protocol (MCP)** es un estándar abierto que permite a asistentes de IA como ChatGPT interactuar de forma segura con fuentes de datos externas y herramientas. Piensa en él como un traductor universal entre modelos de IA y tus aplicaciones.

**Conceptos Clave**:

- **Servidor MCP**: Tu aplicación que expone herramientas y datos
- **Cliente MCP**: ChatGPT actúa como el cliente, llamando tus herramientas
- **Herramientas (Tools)**: Funciones que ChatGPT puede ejecutar (como decir hola)
- **Recursos (Resources)**: Datos o UI que ChatGPT puede leer (como HTML de widgets)
- **Transporte**: Cómo se envían los mensajes (usaremos HTTP)

### 1.2 Cómo Funciona la Comunicación MCP

```
┌─────────────┐                    ┌─────────────┐
│   ChatGPT   │                    │  Tu Servidor│
│   (Cliente) │                    │     MCP     │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. "Saluda a María"             │
       ├─────────────────────────────────>│
       │                                  │
       │  2. JSON-RPC: tools/list         │
       ├─────────────────────────────────>│
       │                                  │
       │  3. Retorna: [say_hello]         │
       │<─────────────────────────────────┤
       │                                  │
       │  4. JSON-RPC: tools/call         │
       │     name: "say_hello"            │
       │     args: {name: "María", ...}   │
       ├─────────────────────────────────>│
       │                                  │
       │  5. Resultado: "¡Hola María! 👋" │
       │<─────────────────────────────────┤
       │                                  │
       │  6. Muestra resultado al usuario │
       └──────────────────────────────────┘
```

**El Flujo**:

1. El usuario le pide a ChatGPT que realice una acción
2. ChatGPT descubre las herramientas disponibles vía `tools/list`
3. ChatGPT llama a una herramienta vía `tools/call` con argumentos
4. Tu servidor procesa la solicitud y retorna resultados
5. ChatGPT puede solicitar HTML de widgets vía `resources/read`
6. El widget se muestra al usuario en ChatGPT

### 1.3 Protocolo JSON-RPC 2.0

MCP usa JSON-RPC 2.0 para toda la comunicación. Aquí hay un ejemplo:

**Solicitud** (ChatGPT → Tu Servidor):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "say_hello",
    "arguments": {
      "name": "María",
      "emoji": true
    }
  }
}
```

**Respuesta** (Tu Servidor → ChatGPT):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "¡Hola María! 👋"
      }
    ]
  }
}
```

🎓 **Aprendiste**: MCP es un protocolo estandarizado que usa JSON-RPC 2.0 para la comunicación entre IA y aplicaciones.

---

## Parte 2: Configuración con Nix

### 2.1 ¿Por qué Nix?

Nix proporciona **entornos de desarrollo reproducibles**. Todos en tu equipo obtienen exactamente las mismas herramientas y versiones. Se acabaron los problemas de "funciona en mi máquina".

### 2.2 Prerrequisitos

- **Nix con flakes habilitados** - [Instalar Nix](https://nixos.org/download.html)
- **Editor de código** (VS Code, Vim, etc.)
- **Terminal**
- **Cuenta en ngrok** (gratuita) - [Registrarse en ngrok.com](https://ngrok.com)

### 2.3 Habilitar Nix Flakes

Si aún no has habilitado flakes:

```bash
# Crear directorio de configuración de Nix
mkdir -p ~/.config/nix

# Habilitar flakes
cat > ~/.config/nix/nix.conf <<EOF
experimental-features = nix-command flakes
EOF
```

### 2.4 Crear el Directorio de tu Proyecto

```bash
# Crear directorio del proyecto
mkdir openai-helloworld-app
cd openai-helloworld-app

# Inicializar git
git init
```

### 2.5 Crear el Nix Flake - Paso a Paso

Vamos a construir el archivo `flake.nix` gradualmente, entendiendo cada parte:

**Paso 1: Estructura Básica**

Crea `flake.nix` con la estructura básica de flake:

```nix
{
  description = "Hola Mundo App con integración MCP";

  # Inputs: Dependencias externas para tu flake
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    # Aquí definiremos qué produce tu flake
    { };
}
```

**Qué hace esto:**
- `description`: Describe tu proyecto
- `inputs`: Declara dependencias (nixpkgs para paquetes, flake-utils para soporte multiplataforma)
- `outputs`: Donde definiremos nuestro entorno de desarrollo (vacío por ahora)

**Paso 2: Agregar Soporte Multiplataforma**

Actualiza la sección `outputs` para soportar múltiples plataformas (Linux, macOS, etc.):

```nix
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      {
        # Definiremos nuestro shell de desarrollo aquí
      }
    );
```

**Qué hace esto:**
- `eachDefaultSystem`: Crea outputs para todas las plataformas comunes (x86_64-linux, aarch64-darwin, etc.)
- `pkgs`: Importa nixpkgs para el sistema actual

**Paso 3: Permitir Paquetes No Libres (para ngrok)**

ngrok es software propietario. Necesitamos permitir paquetes no libres:

```nix
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;  # Requerido para ngrok
          };
        };
      in
```

**Qué hace esto:**
- `allowUnfree = true`: Permite la instalación de software propietario como ngrok

**Paso 4: Definir Herramientas de Desarrollo**

Ahora agreguemos el shell de desarrollo con todas las herramientas necesarias:

```nix
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
```

**Qué hace cada herramienta:**
- **python311**: Intérprete Python 3.11
- **pip & virtualenv**: Gestión de paquetes Python
- **uv**: Gestor de paquetes Python rápido (alternativa a pip)
- **just**: Task runner (como make, pero más simple)
- **ngrok**: Herramienta de túneles para exponer servidor local a internet
- **curl**: Cliente HTTP para pruebas
- **jq**: Procesador JSON para debugging
- **git**: Control de versiones

**Paso 5: Agregar Mensaje de Bienvenida**

Agrega un shellHook que muestre información útil al entrar al entorno:

```nix
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
```

**Qué hace esto:**
- Muestra versiones de herramientas al entrar al shell
- Muestra comandos `just` disponibles
- Configura automáticamente direnv si está instalado

**`flake.nix` Completo:**

```nix
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
```

### 2.6 Entrar al Shell de Desarrollo Nix

```bash
nix develop
```

Deberías ver el mensaje de bienvenida con todas las herramientas disponibles.

🎓 **Aprendiste**:
- Cómo crear un flake Nix para entornos de desarrollo reproducibles
- Qué hace cada herramienta de desarrollo y por qué la necesitamos
- Cómo configurar paquetes no libres
- Cómo agregar shell hooks útiles

### 2.7 Crear pyproject.toml - Paso a Paso

El archivo `pyproject.toml` define la configuración de tu proyecto Python y las dependencias. Construyámoslo sección por sección:

**Paso 1: Metadatos del Proyecto**

Crea `pyproject.toml` con información básica del proyecto:

```toml
[project]
name = "helloworld-app"
version = "0.1.0"
description = "Tutorial Hola Mundo con integración MCP para ChatGPT"
requires-python = ">=3.11"
```

**Qué hace esto:**
- `name`: Nombre de tu proyecto (usado al instalar)
- `version`: Número de versión actual
- `description`: Breve descripción del proyecto
- `requires-python`: Versión mínima de Python requerida

**Paso 2: Dependencias Principales**

Agrega las dependencias principales que tu app necesita:

```toml
dependencies = [
    "fastapi>=0.115.0",           # Framework web para construir APIs
    "uvicorn[standard]>=0.32.0",  # Servidor ASGI para ejecutar FastAPI
    "mcp[fastapi]>=0.1.0",        # Biblioteca Model Context Protocol
    "pydantic>=2.9.0",            # Validación de datos usando type hints
    "python-dotenv>=1.0.0",       # Cargar variables de entorno desde .env
]
```

**Qué hace cada dependencia:**
- **fastapi**: Framework web moderno para construir APIs con documentación OpenAPI automática
- **uvicorn**: Servidor ASGI ultra-rápido para ejecutar tu app FastAPI
- **mcp[fastapi]**: Biblioteca oficial de MCP con integración FastAPI
- **pydantic**: Validación de datos usando type hints de Python (requerido por FastAPI)
- **python-dotenv**: Carga configuración desde archivos `.env`

**Paso 3: Sistema de Construcción**

Define cómo construir tu paquete:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Qué hace esto:**
- Especifica que usamos `hatchling` para construir el paquete
- Backend de construcción moderno (alternativa a setuptools)

**Paso 4: Configuración de Construcción Hatchling**

Configura hatchling para encontrar tu paquete:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/helloworld_app"]  # Decirle a hatchling dónde encontrar el paquete
```

**Qué hace esto:**
- Le dice a hatchling que busque el código en `src/helloworld_app/`
- Esto sigue la convención moderna de layout `src/`

**`pyproject.toml` Completo:**

```toml
[project]
name = "helloworld-app"
version = "0.1.0"
description = "Tutorial Hola Mundo con integración MCP para ChatGPT"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "mcp[fastapi]>=0.1.0",
    "pydantic>=2.9.0",
    "python-dotenv>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/helloworld_app"]
```

🎓 **Aprendiste**:
- Cómo estructurar un archivo `pyproject.toml`
- Qué dependencias necesitas para una app MCP básica
- Cómo configurar el sistema de construcción

### 2.8 Crear .env.example

Antes de crear el `justfile`, necesitamos crear el archivo `.env.example` que el justfile va a copiar.

**Crear `.env.example`:**

```bash
# URL pública de tu aplicación
# Durante desarrollo local:
PUBLIC_URL=http://localhost:8000

# Cuando uses ngrok, cambiarás esto a:
# PUBLIC_URL=https://tu-url-ngrok.ngrok.app
```

**Qué hace esto:**
- Define la URL pública de tu aplicación
- Se usará para que los widgets sepan dónde llamar las APIs
- Durante desarrollo local usa `localhost:8000`
- Cuando uses ngrok, actualizarás esta URL en `.env` (no en `.env.example`)

🎓 **Aprendiste**:
- Para qué sirve el archivo `.env.example`
- Qué variables de entorno necesita tu app
- La diferencia entre `.env.example` (template) y `.env` (valores reales)

### 2.9 Crear .gitignore

También necesitamos crear `.gitignore` para evitar commitear archivos sensibles o generados:

**Crear `.gitignore`:**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# Environment variables
.env

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# uv
uv.lock

# Nix
.direnv/
result
```

**Qué hace esto:**
- Ignora archivos generados por Python (`__pycache__`, `*.pyc`)
- Ignora el entorno virtual (`.venv/`)
- **Importante**: Ignora `.env` (que contiene configuración local/sensible)
- No ignora `.env.example` (que es el template que sí se commitea)

### 2.10 Crear justfile - Paso a Paso

El `justfile` es como un Makefile pero más simple. Define comandos útiles para tu proyecto.

**Requerimientos previos:**
Antes de crear el `justfile`, asegúrate de tener:
- ✅ `pyproject.toml` (creado en sección 2.7)
- ✅ `.env.example` (creado en sección 2.8)
- ✅ Entorno Nix activo (entrado con `nix develop` en sección 2.6)

**Paso 1: Comando de Inicialización**

Crea `justfile` con un comando para inicializar el proyecto:

```makefile
# Inicializar el proyecto (primera vez)
init:
    @echo "📦 Creando entorno virtual..."
    uv venv
    @echo "📥 Instalando dependencias..."
    uv sync
    @echo "📝 Configurando variables de entorno..."
    cp .env.example .env
    @echo "✅ Proyecto inicializado. Usa 'just dev' para empezar."
```

**Qué hace esto:**
- Crea un entorno virtual Python con `uv venv`
- Instala las dependencias con `uv sync`
- Copia el template de variables de entorno
- El `@` hace que no se muestre el comando, solo el output

**Paso 2: Comando de Desarrollo**

Agrega comando para iniciar el servidor de desarrollo:

```makefile
# Iniciar servidor de desarrollo
dev:
    @echo "🚀 Iniciando servidor de desarrollo..."
    uv run uvicorn src.helloworld_app.main:app --reload --host 0.0.0.0 --port 8000
```

**Qué hace esto:**
- Usa `uv run` para ejecutar uvicorn en el entorno virtual
- `--reload`: Reinicia automáticamente cuando cambias código
- `--host 0.0.0.0`: Permite conexiones desde cualquier interfaz
- `--port 8000`: Escucha en el puerto 8000

**Paso 3: Comando de Túnel**

Agrega comando para iniciar ngrok:

```makefile
# Iniciar túnel ngrok
tunnel:
    @echo "🌍 Iniciando túnel ngrok..."
    @echo "⚠️  Copia la URL HTTPS y actualiza PUBLIC_URL en .env"
    ngrok http 8000
```

**Qué hace esto:**
- Inicia ngrok para exponer tu servidor local
- Muestra recordatorio para actualizar la variable de entorno

**Paso 4: Comando de Información**

Agrega comando para mostrar información útil:

```makefile
# Mostrar información del proyecto
info:
    @echo "👋 Hola Mundo App"
    @echo "═══════════════════════════════════"
    @echo "📍 Servidor: http://localhost:8000"
    @echo "📍 MCP Endpoint: http://localhost:8000/mcp"
    @echo "📍 Docs API: http://localhost:8000/docs"
    @echo ""
    @echo "Comandos disponibles:"
    @echo "  just init    - Inicializar proyecto"
    @echo "  just dev     - Servidor de desarrollo"
    @echo "  just tunnel  - Iniciar ngrok"
    @echo "  just info    - Mostrar esta información"
```

**`justfile` Completo:**

```makefile
# Inicializar el proyecto (primera vez)
init:
    @echo "📦 Creando entorno virtual..."
    uv venv
    @echo "📥 Instalando dependencias..."
    uv sync
    @echo "📝 Configurando variables de entorno..."
    cp .env.example .env
    @echo "✅ Proyecto inicializado. Usa 'just dev' para empezar."

# Iniciar servidor de desarrollo
dev:
    @echo "🚀 Iniciando servidor de desarrollo..."
    uv run uvicorn src.helloworld_app.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar túnel ngrok
tunnel:
    @echo "🌍 Iniciando túnel ngrok..."
    @echo "⚠️  Copia la URL HTTPS y actualiza PUBLIC_URL en .env"
    ngrok http 8000

# Mostrar información del proyecto
info:
    @echo "👋 Hola Mundo App"
    @echo "═══════════════════════════════════"
    @echo "📍 Servidor: http://localhost:8000"
    @echo "📍 MCP Endpoint: http://localhost:8000/mcp"
    @echo "📍 Docs API: http://localhost:8000/docs"
    @echo ""
    @echo "Comandos disponibles:"
    @echo "  just init    - Inicializar proyecto"
    @echo "  just dev     - Servidor de desarrollo"
    @echo "  just tunnel  - Iniciar ngrok"
    @echo "  just info    - Mostrar esta información"
```

🎓 **Aprendiste**:
- Cómo crear un `justfile` para automatizar tareas
- Comandos útiles para desarrollo
- Cómo usar `uv` para gestionar dependencias
- Qué archivos necesita el `justfile` para funcionar correctamente

### 2.11 Inicializar el Proyecto

Ahora que todos los archivos de configuración están listos, podemos inicializar el proyecto:

```bash
# Inicializar el proyecto (crea .env, instala dependencias)
just init
```

**Esto:**
1. Crea el entorno virtual con `uv venv`
2. Instala las dependencias definidas en `pyproject.toml`
3. Copia `.env.example` a `.env` para configuración local

**Salida esperada:**
```
📦 Creando entorno virtual...
📥 Instalando dependencias...
📝 Configurando variables de entorno...
✅ Proyecto inicializado. Usa 'just dev' para empezar.
```

🎓 **Aprendiste**:
- El orden correcto de inicialización del proyecto
- Cómo `uv` gestiona entornos virtuales y dependencias
- La diferencia entre archivos de configuración (template) y archivos locales

---

## Parte 3: Construyendo el Servidor MCP

### 3.1 Crear la Estructura del Proyecto

```bash
# Crear estructura de carpetas
mkdir -p src/helloworld_app

# Crear archivos vacíos
touch src/helloworld_app/__init__.py
touch src/helloworld_app/main.py
touch src/helloworld_app/mcp_server.py
```

Tu estructura quedará así:

```
openai-helloworld-app/
├── flake.nix
├── pyproject.toml
├── justfile
└── src/
    └── helloworld_app/
        ├── __init__.py      # Marca el paquete Python
        ├── main.py          # FastAPI + integración MCP
        └── mcp_server.py    # Lógica MCP
```

### 3.2 Crear el Módulo Python

Edita `src/helloworld_app/__init__.py`:

```python
"""Hola Mundo App - Tutorial básico de OpenAI Apps SDK."""

__version__ = "0.1.0"
```

**Qué hace esto:**
- Define el paquete Python
- Declara la versión de la aplicación

### 3.3 Crear el Servidor MCP - Paso a Paso

Ahora viene la magia. Vamos a construir `src/helloworld_app/mcp_server.py` paso a paso:

**Paso 1: Imports y Creación del Servidor**

```python
"""Servidor MCP simple - Solo dice Hola."""

from mcp import FastMCP
from pydantic import BaseModel, Field
import os

# 1. Crear el servidor MCP
mcp = FastMCP("Hola Mundo App")
```

**Qué hace esto:**
- Importa `FastMCP` para crear el servidor MCP
- Importa `Pydantic` para validación de datos
- Crea una instancia del servidor MCP con un nombre

**Paso 2: Definir el Modelo de Entrada**

```python
# 2. Definir el modelo de entrada para la herramienta
class SayHelloInput(BaseModel):
    """Entrada para decir hola."""
    name: str = Field(description="Nombre de la persona a saludar")
    emoji: bool = Field(default=True, description="¿Incluir emoji?")
```

**Qué hace esto:**
- Define qué parámetros acepta nuestra herramienta
- Usa Pydantic para validación automática
- `Field()` proporciona descripciones para ChatGPT

**Paso 3: Crear la Herramienta MCP**

```python
# 3. Crear una herramienta MCP
@mcp.tool()
def say_hello(input: SayHelloInput) -> str:
    """Dice hola a alguien de manera amigable.

    Esta es la función que ChatGPT puede llamar.
    """
    greeting = f"¡Hola {input.name}!"
    if input.emoji:
        greeting += " 👋"

    return greeting
```

**Qué hace esto:**
- El decorador `@mcp.tool()` registra la función como herramienta MCP
- ChatGPT puede llamar esta función cuando el usuario lo solicite
- Retorna un string simple con el saludo

**Paso 4: Crear el Widget HTML**

```python
# 4. Crear un widget HTML simple
@mcp.resource("ui://widget/hello.html")
def show_hello_widget() -> str:
    """Widget visual que muestra la aplicación de saludos."""

    # Obtener la URL pública (para llamadas API)
    public_url = os.getenv("PUBLIC_URL", "http://localhost:8000")

    # HTML auto-contenido con estilos y JavaScript
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hola Mundo</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}

        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }}

        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}

        .input-group {{
            margin-bottom: 20px;
        }}

        label {{
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }}

        input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }}

        input[type="text"]:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .checkbox-group {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}

        input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
        }}

        button {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }}

        button:active {{
            transform: translateY(0);
        }}

        .result {{
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
            font-size: 24px;
            font-weight: 500;
            color: #333;
            display: none;
        }}

        .result.show {{
            display: block;
            animation: fadeIn 0.5s;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .info-box {{
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            border-radius: 5px;
            font-size: 13px;
            color: #1976d2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>👋 Hola Mundo</h1>
        <p class="subtitle">Tutorial de OpenAI Apps SDK</p>

        <div class="input-group">
            <label for="nameInput">¿A quién quieres saludar?</label>
            <input
                type="text"
                id="nameInput"
                placeholder="Ej: María, Juan, Claude..."
                value="Mundo"
            />
        </div>

        <div class="checkbox-group">
            <input type="checkbox" id="emojiCheck" checked />
            <label for="emojiCheck">Incluir emoji 👋</label>
        </div>

        <button onclick="sayHello()">¡Saludar!</button>

        <div id="result" class="result"></div>

        <div class="info-box">
            <strong>💡 Cómo funciona:</strong><br>
            Este widget llama a la herramienta MCP "say_hello" cuando haces clic en el botón.
        </div>
    </div>

    <script>
        // Esta función se ejecuta cuando haces clic en "¡Saludar!"
        async function sayHello() {{
            const name = document.getElementById('nameInput').value;
            const emoji = document.getElementById('emojiCheck').checked;
            const resultDiv = document.getElementById('result');

            // Mostrar "Cargando..."
            resultDiv.textContent = '⏳ Generando saludo...';
            resultDiv.classList.add('show');

            try {{
                // IMPORTANTE: Usar window.openai para llamar herramientas MCP
                // Esto es específico de OpenAI Apps SDK
                const result = await window.openai.callTool({{
                    name: 'say_hello',  // Nombre de la herramienta MCP
                    parameters: {{
                        name: name,
                        emoji: emoji
                    }}
                }});

                // Mostrar el resultado
                resultDiv.textContent = result;

            }} catch (error) {{
                resultDiv.textContent = '❌ Error: ' + error.message;
                console.error('Error:', error);
            }}
        }}

        // Permitir presionar Enter en el input
        document.getElementById('nameInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                sayHello();
            }}
        }});
    </script>
</body>
</html>
    """

    return html
```

**Qué hace esto:**
- El decorador `@mcp.resource()` registra el widget con un URI único
- Genera HTML con CSS y JavaScript embebidos
- Usa `window.openai.callTool()` para llamar la herramienta MCP desde JavaScript
- El widget es completamente auto-contenido (no necesita archivos externos)

**Archivo `src/helloworld_app/mcp_server.py` Completo:**

<detalles>
<summary>Ver código completo de mcp_server.py</summary>

```python
"""Servidor MCP simple - Solo dice Hola."""

from mcp import FastMCP
from pydantic import BaseModel, Field
import os

# 1. Crear el servidor MCP
mcp = FastMCP("Hola Mundo App")

# 2. Definir el modelo de entrada para la herramienta
class SayHelloInput(BaseModel):
    """Entrada para decir hola."""
    name: str = Field(description="Nombre de la persona a saludar")
    emoji: bool = Field(default=True, description="¿Incluir emoji?")

# 3. Crear una herramienta MCP
@mcp.tool()
def say_hello(input: SayHelloInput) -> str:
    """Dice hola a alguien de manera amigable.

    Esta es la función que ChatGPT puede llamar.
    """
    greeting = f"¡Hola {input.name}!"
    if input.emoji:
        greeting += " 👋"

    return greeting

# 4. Crear un widget HTML simple
@mcp.resource("ui://widget/hello.html")
def show_hello_widget() -> str:
    """Widget visual que muestra la aplicación de saludos."""

    # Obtener la URL pública (para llamadas API)
    public_url = os.getenv("PUBLIC_URL", "http://localhost:8000")

    # HTML auto-contenido con estilos y JavaScript
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hola Mundo</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}

        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }}

        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}

        .input-group {{
            margin-bottom: 20px;
        }}

        label {{
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }}

        input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }}

        input[type="text"]:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .checkbox-group {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}

        input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
        }}

        button {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }}

        button:active {{
            transform: translateY(0);
        }}

        .result {{
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
            font-size: 24px;
            font-weight: 500;
            color: #333;
            display: none;
        }}

        .result.show {{
            display: block;
            animation: fadeIn 0.5s;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .info-box {{
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            border-radius: 5px;
            font-size: 13px;
            color: #1976d2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>👋 Hola Mundo</h1>
        <p class="subtitle">Tutorial de OpenAI Apps SDK</p>

        <div class="input-group">
            <label for="nameInput">¿A quién quieres saludar?</label>
            <input
                type="text"
                id="nameInput"
                placeholder="Ej: María, Juan, Claude..."
                value="Mundo"
            />
        </div>

        <div class="checkbox-group">
            <input type="checkbox" id="emojiCheck" checked />
            <label for="emojiCheck">Incluir emoji 👋</label>
        </div>

        <button onclick="sayHello()">¡Saludar!</button>

        <div id="result" class="result"></div>

        <div class="info-box">
            <strong>💡 Cómo funciona:</strong><br>
            Este widget llama a la herramienta MCP "say_hello" cuando haces clic en el botón.
        </div>
    </div>

    <script>
        // Esta función se ejecuta cuando haces clic en "¡Saludar!"
        async function sayHello() {{
            const name = document.getElementById('nameInput').value;
            const emoji = document.getElementById('emojiCheck').checked;
            const resultDiv = document.getElementById('result');

            // Mostrar "Cargando..."
            resultDiv.textContent = '⏳ Generando saludo...';
            resultDiv.classList.add('show');

            try {{
                // IMPORTANTE: Usar window.openai para llamar herramientas MCP
                // Esto es específico de OpenAI Apps SDK
                const result = await window.openai.callTool({{
                    name: 'say_hello',  // Nombre de la herramienta MCP
                    parameters: {{
                        name: name,
                        emoji: emoji
                    }}
                }});

                // Mostrar el resultado
                resultDiv.textContent = result;

            }} catch (error) {{
                resultDiv.textContent = '❌ Error: ' + error.message;
                console.error('Error:', error);
            }}
        }}

        // Permitir presionar Enter en el input
        document.getElementById('nameInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                sayHello();
            }}
        }});
    </script>
</body>
</html>
    """

    return html
```
</detalles>

🎓 **Aprendiste**:
- Cómo crear un servidor MCP con `FastMCP`
- Cómo definir herramientas con `@mcp.tool()`
- Cómo crear widgets con `@mcp.resource()`
- Cómo usar `window.openai.callTool()` en JavaScript

### 3.4 Crear la Aplicación FastAPI

Ahora creamos `src/helloworld_app/main.py`:

```python
"""Aplicación FastAPI que expone el servidor MCP."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Importar nuestro servidor MCP
from .mcp_server import mcp

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(
    title="Hola Mundo App",
    description="Tutorial básico de OpenAI Apps SDK",
    version="0.1.0"
)

# CORS: Permite que ChatGPT hable con tu app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar el servidor MCP en /mcp
# Este es el endpoint que ChatGPT usará
app.mount("/mcp", mcp.get_asgi_app())

# Endpoint de salud (opcional, pero útil)
@app.get("/")
async def root():
    return {
        "message": "Hola Mundo App está corriendo",
        "mcp_endpoint": "/mcp",
        "status": "ok"
    }

# Para ejecutar directamente con Python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Qué hace esto:**
- Crea una aplicación FastAPI
- Configura CORS para permitir solicitudes desde ChatGPT
- Monta el servidor MCP en el endpoint `/mcp`
- Proporciona un endpoint de salud en `/`

🎓 **Aprendiste**:
- Cómo integrar un servidor MCP con FastAPI
- Por qué necesitamos CORS
- Cómo montar el servidor MCP en un endpoint
- La estructura completa de un proyecto MCP

---

## Parte 4: Probando Localmente

**⚠️ Prerequisitos:**
Antes de continuar con esta sección, asegúrate de haber completado la **Parte 3 completa**:
- ✅ Estructura de carpetas creada (sección 3.1): `src/helloworld_app/`
- ✅ Archivo `__init__.py` creado (sección 3.2)
- ✅ Archivo `mcp_server.py` creado (sección 3.3)
- ✅ Archivo `main.py` creado (sección 3.4)

Si ejecutas `just dev` sin estos archivos, obtendrás el error: `ModuleNotFoundError: No module named 'src'`

### 4.1 Iniciar el Servidor

```bash
just dev
```

Deberías ver:

```
🚀 Iniciando servidor de desarrollo...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

**¡Felicidades! Tu servidor MCP está corriendo.** 🎉

### 4.2 Verificar que el Servidor Está Vivo

Abre otra terminal y ejecuta:

```bash
curl http://localhost:8000/
```

Deberías ver:

```json
{
  "message": "Hola Mundo App está corriendo",
  "mcp_endpoint": "/mcp",
  "status": "ok"
}
```

### 4.3 Listar Herramientas MCP Disponibles

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

Deberías ver la herramienta `say_hello` listada con su esquema.

### 4.4 Llamar la Herramienta Directamente

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "say_hello",
      "arguments": {
        "name": "Claude",
        "emoji": true
      }
    },
    "id": 2
  }'
```

Deberías ver:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "¡Hola Claude! 👋"
      }
    ]
  }
}
```

### 4.5 Probar Diferentes Parámetros

```bash
# Sin emoji
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "say_hello",
      "arguments": {
        "name": "María",
        "emoji": false
      }
    },
    "id": 3
  }'
```

Resultado: `¡Hola María!` (sin emoji)

🎓 **Aprendiste**:
- Cómo probar tu servidor MCP localmente
- El formato de solicitudes JSON-RPC 2.0
- Cómo llamar herramientas MCP directamente con curl

---

## Parte 5: Conectando con ChatGPT

### 5.1 Exponer con ngrok

Para que ChatGPT pueda acceder a tu servidor local, necesitas exponerlo a Internet:

**En una nueva terminal:**

```bash
just tunnel
```

O directamente:

```bash
ngrok http 8000
```

Verás algo como:

```
Forwarding   https://abc123-45-67-89-10.ngrok-free.app -> http://localhost:8000
```

**Copia esa URL de ngrok** (ej: `https://abc123-45-67-89-10.ngrok-free.app`)

### 5.2 Actualizar Variables de Entorno

Edita `.env`:

```bash
PUBLIC_URL=https://abc123-45-67-89-10.ngrok-free.app
```

**Reinicia el servidor** (Ctrl+C en la terminal del servidor, luego `just dev`)

### 5.3 Verificar que ngrok Funciona

```bash
# Usa tu URL de ngrok
curl https://abc123-45-67-89-10.ngrok-free.app/
```

Deberías ver el mismo mensaje de antes. ✅

### 5.4 Ir a OpenAI Platform

1. Visita: https://platform.openai.com/playground/apps
2. Click en "Create App"
3. Llena el formulario:
   - **Name**: Hola Mundo App
   - **Description**: Tutorial básico de MCP
   - **MCP Server URL**: `https://tu-url-ngrok.ngrok-free.app/mcp` (⚠️ no olvides el `/mcp`)

4. Click en "Create"

### 5.5 Probar en ChatGPT

Ahora en ChatGPT, puedes decir:

**Ejemplo 1: Llamar la herramienta**
```
"Usa la app Hola Mundo para saludar a María"
```

ChatGPT debería:
1. Llamar a tu herramienta `say_hello`
2. Recibir `¡Hola María! 👋`
3. Mostrarte el resultado

**Ejemplo 2: Mostrar el widget**
```
"Muéstrame el widget de Hola Mundo"
```

ChatGPT mostrará tu interfaz HTML interactiva donde puedes:
- Escribir un nombre
- Elegir si quieres emoji
- Hacer clic en "¡Saludar!"
- Ver el resultado

🎓 **Aprendiste**:
- Cómo exponer tu servidor local con ngrok
- Cómo registrar tu app en OpenAI Platform
- Cómo probar tu app en ChatGPT

---

## 🎓 Resumen: ¿Qué Aprendiste?

### Conceptos

- ✅ **MCP (Model Context Protocol)**: Protocolo para que ChatGPT se comunique con aplicaciones
- ✅ **JSON-RPC 2.0**: Formato de mensajes que usa MCP
- ✅ **Herramientas MCP**: Funciones que ChatGPT puede llamar
- ✅ **Recursos MCP**: Contenido (como widgets HTML) que ChatGPT puede leer
- ✅ **window.openai API**: API JavaScript para widgets

### Habilidades Técnicas

- ✅ Configurar entorno reproducible con Nix
- ✅ Gestionar dependencias con `pyproject.toml` y `uv`
- ✅ Crear servidor MCP con FastMCP
- ✅ Definir herramientas con `@mcp.tool()`
- ✅ Crear widgets con `@mcp.resource()`
- ✅ Integrar MCP con FastAPI
- ✅ Probar con curl y JSON-RPC
- ✅ Exponer servidor con ngrok
- ✅ Registrar app en OpenAI Platform

### Flujo Completo

```
Usuario en ChatGPT
    ↓
ChatGPT analiza la solicitud
    ↓
ChatGPT llama tools/list
    ↓
Tu servidor responde con herramientas disponibles
    ↓
ChatGPT llama tools/call con say_hello
    ↓
Tu servidor Python ejecuta la función
    ↓
Respuesta vuelve a ChatGPT
    ↓
ChatGPT muestra el resultado al usuario
```

---

## 🚀 Siguientes Pasos

Ahora que entiendes lo básico, puedes:

### Nivel 1: Modificaciones Simples

- Cambia el emoji por otros: 🎉, 🌟, 💫
- Añade más parámetros: idioma, hora del día (buenos días/tardes/noches)
- Cambia los colores del widget
- Modifica los estilos CSS

### Nivel 2: Nueva Herramienta

- Añade una herramienta `farewell` que se despida
- Crea un widget para despedidas
- Prueba con ChatGPT

### Nivel 3: Con Datos

- Lee el [Tutorial de ToDo App](./todo-app-tutorial.md) para ver una app completa
- Aprende a guardar datos (CRUD)
- Crea APIs REST

### Nivel 4: Construcción Desde Cero

- Sigue el [Tutorial de Notes App](./notes-app-tutorial.md)
- Construye desde cero con explicaciones profundas
- Ve la evolución de simple a complejo

---

## 🐛 Troubleshooting

### Error: "Module not found"

```bash
# Asegúrate de instalar las dependencias
just init

# Verifica que estás en el directorio correcto
pwd  # Debería mostrar .../openai-helloworld-app

# Activa el entorno virtual si es necesario
source .venv/bin/activate
```

### Error: "Address already in use"

```bash
# El puerto 8000 ya está en uso
# Encuentra y mata el proceso:
lsof -ti:8000 | xargs kill -9

# O usa otro puerto:
uv run uvicorn src.helloworld_app.main:app --reload --port 8001
```

### Widget No Se Conecta con MCP

1. Verifica que `PUBLIC_URL` en `.env` es tu URL de ngrok
2. Reinicia el servidor después de cambiar `.env`
3. Verifica que ngrok está corriendo en otra terminal
4. Asegúrate que la URL termina sin `/mcp` en `.env`

### ChatGPT No Ve Mi App

1. Verifica que la URL de ngrok es correcta
2. Asegúrate de agregar `/mcp` al final al registrar: `https://tu-url.ngrok.app/mcp`
3. Verifica que CORS está habilitado (ya está en el código)
4. Prueba llamar `https://tu-url.ngrok.app/mcp` con curl primero

### ngrok Dice "Session Expired"

```bash
# ngrok free tiene límite de 8 horas
# Simplemente reinicia ngrok y actualiza la URL en:
# 1. .env -> PUBLIC_URL
# 2. OpenAI Platform -> MCP Server URL
# 3. Reinicia el servidor
```

---

## 📚 Recursos Adicionales

### Tutoriales

- [Tutorial de ToDo App](./todo-app-tutorial.md) - App completa con CRUD
- [Tutorial de Notes App](./notes-app-tutorial.md) - Construcción desde cero

### Documentación

- [EXPLANATION.md](../EXPLANATION.md) - Conceptos profundos de MCP
- [GUIDE.md](../GUIDE.md) - Guías de referencia
- [MCP Specification](https://modelcontextprotocol.io/) - Especificación oficial
- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk/) - Documentación de OpenAI

### Herramientas

- [FastAPI Docs](https://fastapi.tiangolo.com/) - Framework web
- [Pydantic Docs](https://docs.pydantic.dev/) - Validación de datos
- [uv Docs](https://docs.astral.sh/uv/) - Gestor de paquetes
- [Nix Flakes](https://nixos.wiki/wiki/Flakes) - Entornos reproducibles

---

## ✅ Checklist de Completitud

- [ ] Entiendo qué es MCP y cómo funciona
- [ ] Sé cómo crear un flake.nix para entornos reproducibles
- [ ] Entiendo cómo estructurar pyproject.toml
- [ ] Sé crear una herramienta con `@mcp.tool()`
- [ ] Sé crear un widget con `@mcp.resource()`
- [ ] Entiendo el flujo: ChatGPT → MCP → Python → Respuesta
- [ ] Sé usar `window.openai.callTool()` en JavaScript
- [ ] He probado mi servidor localmente con curl
- [ ] Sé usar ngrok para exponer mi servidor
- [ ] He conectado mi app con ChatGPT
- [ ] He visto el widget funcionando en ChatGPT

---

## 🎉 ¡Felicidades!

Has completado tu primera app con OpenAI Apps SDK. Ahora entiendes:

- Cómo MCP conecta ChatGPT con tu código
- Cómo crear herramientas que ChatGPT puede usar
- Cómo crear UIs interactivas con widgets
- El flujo completo de datos
- Cómo configurar entornos reproducibles con Nix

**Estás listo para construir apps más complejas.** 🚀

---

**¿Preguntas?** Revisa la documentación o prueba los otros tutoriales.

**Siguiente**: [Tutorial de ToDo App](./todo-app-tutorial.md) para ver una app completa con base de datos.
