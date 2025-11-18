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
      "input": {
        "name": "María",
        "emoji": true
      }
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
    "fastapi>=0.115.0",           # Incluye Starlette (framework ASGI usado por MCP)
    "uvicorn[standard]>=0.32.0",  # Servidor ASGI para ejecutar la aplicación
    "mcp[fastapi]>=0.1.0",        # Biblioteca Model Context Protocol
    "pydantic>=2.9.0",            # Validación de datos usando type hints
    "python-dotenv>=1.0.0",       # Cargar variables de entorno desde .env
]
```

**Qué hace cada dependencia:**
- **fastapi**: Incluye Starlette, el framework ASGI que usaremos (MCP crea una aplicación Starlette)
- **uvicorn**: Servidor ASGI ultra-rápido para ejecutar la aplicación
- **mcp[fastapi]**: Biblioteca oficial de MCP con todas las dependencias necesarias
- **pydantic**: Validación de datos usando type hints de Python
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

El `justfile` es como un Makefile pero más simple. Define comandos útiles para tu proyecto. Vamos a crearlo **incrementalmente**, validando cada comando antes de agregar el siguiente.

#### 2.10.1 Comando `info` - Primer Paso

**Prerequisitos:**
- ✅ Ninguno (este comando solo imprime información)

**Crear `justfile`** con el primer comando:

```makefile
# Mostrar información del proyecto
info:
    @echo "👋 Hola Mundo App"
    @echo "═══════════════════════════════════"
    @echo "📍 Servidor: http://localhost:8000"
    @echo "📍 MCP Endpoint: http://localhost:8000/mcp"
    @echo "📍 Docs API: http://localhost:8000/docs"
```

**Qué hace esto:**
- El `@` oculta el comando y solo muestra el output
- Imprime información útil sobre el proyecto

**✅ Validar ahora:**

```bash
just info
```

**Salida esperada:**
```
👋 Hola Mundo App
═══════════════════════════════════
📍 Servidor: http://localhost:8000
📍 MCP Endpoint: http://localhost:8000/mcp
📍 Docs API: http://localhost:8000/docs
```

Si ves este output, ¡tu `justfile` funciona! ✅

#### 2.10.2 Comando `init` - Inicializar Proyecto

**Prerequisitos:**
- ✅ `pyproject.toml` (creado en sección 2.7)
- ✅ `.env.example` (creado en sección 2.8)
- ✅ Entorno Nix activo (entrado con `nix develop` en sección 2.6)

**Agregar** el comando `init` a tu `justfile`:

```makefile
# Mostrar información del proyecto
info:
    @echo "👋 Hola Mundo App"
    @echo "═══════════════════════════════════"
    @echo "📍 Servidor: http://localhost:8000"
    @echo "📍 MCP Endpoint: http://localhost:8000/mcp"
    @echo "📍 Docs API: http://localhost:8000/docs"

# Inicializar el proyecto (primera vez)
init:
    @echo "📦 Creando entorno virtual..."
    uv venv
    @echo "📥 Instalando dependencias..."
    uv sync
    @echo "📝 Configurando variables de entorno..."
    cp .env.example .env
    @echo "✅ Proyecto inicializado."
```

**Qué hace esto:**
- `uv venv`: Crea un entorno virtual Python en `.venv/`
- `uv sync`: Instala dependencias desde `pyproject.toml`
- `cp .env.example .env`: Copia template de variables de entorno

**✅ Validar ahora:**

```bash
just init
```

**Salida esperada:**
```
📦 Creando entorno virtual...
📥 Instalando dependencias...
📝 Configurando variables de entorno...
✅ Proyecto inicializado.
```

**Verificar que se crearon los archivos:**
```bash
ls -la .venv/    # Debe existir el entorno virtual
ls -la .env      # Debe existir el archivo .env
```

Si ves estos archivos, ¡tu proyecto está inicializado! ✅

#### 2.10.3 Comando `tunnel` - Para Más Adelante

**Prerequisitos:**
- ✅ ngrok instalado (ya está en tu entorno Nix)

**Agregar** el comando `tunnel` a tu `justfile`:

```makefile
# Mostrar información del proyecto
info:
    @echo "👋 Hola Mundo App"
    @echo "═══════════════════════════════════"
    @echo "📍 Servidor: http://localhost:8000"
    @echo "📍 MCP Endpoint: http://localhost:8000/mcp"
    @echo "📍 Docs API: http://localhost:8000/docs"

# Inicializar el proyecto (primera vez)
init:
    @echo "📦 Creando entorno virtual..."
    uv venv
    @echo "📥 Instalando dependencias..."
    uv sync
    @echo "📝 Configurando variables de entorno..."
    cp .env.example .env
    @echo "✅ Proyecto inicializado."

# Iniciar túnel ngrok
tunnel:
    @echo "🌍 Iniciando túnel ngrok..."
    @echo "⚠️  Copia la URL HTTPS y actualiza PUBLIC_URL en .env"
    ngrok http 8000
```

**Qué hace esto:**
- Inicia ngrok para exponer tu servidor local a Internet
- Necesario para que ChatGPT acceda a tu app en desarrollo

**⏭️ NO validar ahora** (lo haremos en la Parte 5 cuando tengamos el servidor corriendo)

**Tu `justfile` actual debe verse así:**

```makefile
# Mostrar información del proyecto
info:
    @echo "👋 Hola Mundo App"
    @echo "═══════════════════════════════════"
    @echo "📍 Servidor: http://localhost:8000"
    @echo "📍 MCP Endpoint: http://localhost:8000/mcp"
    @echo "📍 Docs API: http://localhost:8000/docs"

# Inicializar el proyecto (primera vez)
init:
    @echo "📦 Creando entorno virtual..."
    uv venv
    @echo "📥 Instalando dependencias..."
    uv sync
    @echo "📝 Configurando variables de entorno..."
    cp .env.example .env
    @echo "✅ Proyecto inicializado."

# Iniciar túnel ngrok
tunnel:
    @echo "🌍 Iniciando túnel ngrok..."
    @echo "⚠️  Copia la URL HTTPS y actualiza PUBLIC_URL en .env"
    ngrok http 8000
```

🎓 **Aprendiste**:
- Cómo crear un `justfile` incrementalmente
- Validar cada comando antes de continuar
- El comando `info` imprime información útil
- El comando `init` configura tu proyecto
- El comando `tunnel` se usará más adelante

**Nota importante:** El comando `dev` lo agregaremos **después** de crear los archivos Python en la Parte 3, porque requiere que exista `src/helloworld_app/main.py`.

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

from mcp import FastMCP, types
from pydantic import BaseModel, Field
import os

# 1. Crear el servidor MCP
mcp = FastMCP("Hola Mundo App")
```

**Qué hace esto:**
- Importa `FastMCP` y `types` desde el paquete `mcp`
- Importa `Pydantic` para validación de datos
- Importa `os` para leer variables de entorno
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
# 3. Crear la herramienta MCP
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
- FastMCP automáticamente genera el esquema JSON y la descripción de la herramienta

¡Y eso es todo! Con solo 3 pasos tienes una herramienta MCP funcional. Veamos el código completo:

**Archivo `src/helloworld_app/mcp_server.py` Completo:**

```python
"""Servidor MCP simple - Solo dice Hola."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# 1. Crear el servidor MCP
mcp = FastMCP("Hola Mundo App")

# 2. Definir el modelo de entrada para la herramienta
class SayHelloInput(BaseModel):
    """Entrada para decir hola."""
    name: str = Field(description="Nombre de la persona a saludar")
    emoji: bool = Field(default=True, description="¿Incluir emoji?")

# 3. Crear la herramienta MCP
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

**¡Solo 26 líneas de código!** Y ya tienes un servidor MCP completo que ChatGPT puede usar.

🎓 **Aprendiste:**
- Cómo crear un servidor MCP con `FastMCP`
- Cómo definir modelos de entrada con Pydantic
- Cómo usar `@mcp.tool()` para registrar herramientas
- El flujo básico: Usuario → ChatGPT → MCP → Python → Respuesta

**Nota:** Si quieres agregar widgets HTML interactivos a tu app, consulta el tutorial avanzado "Agregando Widgets a tu App MCP" (próximamente).

---

### 3.4 Crear la Aplicación Principal - Paso a Paso

Ahora vamos a crear `src/helloworld_app/main.py` para exponer nuestro servidor MCP via HTTP:

**¿Por qué necesitamos este archivo?**
- `mcp_server.py` define las herramientas
- `main.py` crea la aplicación web que expone esas herramientas en `/mcp`
- ChatGPT se conecta a esta aplicación para usar tus herramientas

**Paso 1: Imports y Configuración Inicial**

Crea `src/helloworld_app/main.py`:

```python
"""Aplicación principal que expone el servidor MCP."""

from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.responses import JSONResponse
from dotenv import load_dotenv

# Importar nuestro servidor MCP
from .mcp_server import mcp

# Cargar variables de entorno desde .env
load_dotenv()
```

**Qué hace esto:**
- Importa componentes de Starlette para crear la app web
- Importa el servidor MCP que definimos
- Carga variables de entorno (como `PUBLIC_URL`)

**Paso 2: Crear Endpoint de Salud**

```python
# Endpoint de salud
async def health_check(request):
    """Endpoint raíz para verificar que el servidor está vivo."""
    return JSONResponse({
        "message": "Hola Mundo App está corriendo",
        "mcp_endpoint": "/mcp",
        "status": "ok"
    })
```

**Qué hace esto:**
- Define una función que responde en la ruta raíz `/`
- Útil para verificar que el servidor está funcionando
- Muestra información sobre dónde está el endpoint MCP

**Paso 3: Obtener la Aplicación del Servidor MCP**

```python
# Obtener la aplicación Starlette del servidor MCP
# Ya incluye el endpoint /mcp configurado automáticamente
app = mcp.streamable_http_app()

# Agregar ruta de salud
app.routes.append(Route("/", health_check))
```

**Qué hace esto:**
- `mcp.streamable_http_app()`: FastMCP crea automáticamente una aplicación Starlette
- El endpoint `/mcp` ya está configurado (no necesitas hacer nada más!)
- Agregamos nuestra ruta de salud en `/`

**Paso 4: Configurar CORS**

```python
# CORS: Permite que ChatGPT hable con tu app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Qué hace esto:**
- CORS (Cross-Origin Resource Sharing) permite que ChatGPT se comunique con tu servidor
- `allow_origins=["*"]`: Permite peticiones desde cualquier origen (⚠️ solo para desarrollo)
- Sin CORS, ChatGPT no podría llamar a tus herramientas

**Archivo `src/helloworld_app/main.py` Completo:**

```python
"""Aplicación principal que expone el servidor MCP."""

from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.responses import JSONResponse
from dotenv import load_dotenv

# Importar nuestro servidor MCP
from .mcp_server import mcp

# Cargar variables de entorno desde .env
load_dotenv()

# Endpoint de salud
async def health_check(request):
    """Endpoint raíz para verificar que el servidor está vivo."""
    return JSONResponse({
        "message": "Hola Mundo App está corriendo",
        "mcp_endpoint": "/mcp",
        "status": "ok"
    })

# Obtener la aplicación Starlette del servidor MCP
# Ya incluye el endpoint /mcp configurado automáticamente
app = mcp.streamable_http_app()

# Agregar ruta de salud
app.routes.append(Route("/", health_check))

# CORS: Permite que ChatGPT hable con tu app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**¡Solo 35 líneas de código!** Y ya tienes una aplicación MCP completa lista para conectar con ChatGPT.

🎓 **Aprendiste:**
- Cómo obtener la app del servidor MCP con `streamable_http_app()`
- Por qué usamos Starlette (FastMCP crea la app por nosotros)
- Que el endpoint `/mcp` se configura automáticamente
- Cómo agregar rutas personalizadas con `app.routes.append()`
- Por qué necesitamos CORS para ChatGPT

---

### 3.5 Agregar Comando `dev` al justfile

Ahora que tenemos todos los archivos Python creados, podemos agregar el comando `dev` al justfile.

**Prerequisitos:**
- ✅ `src/helloworld_app/__init__.py` (creado en sección 3.2)
- ✅ `src/helloworld_app/mcp_server.py` (creado en sección 3.3)
- ✅ `src/helloworld_app/main.py` (creado en sección 3.4)

**Agregar** el comando `dev` a tu `justfile` existente. Tu `justfile` completo debe verse así:

```makefile
# Mostrar información del proyecto
info:
    @echo "👋 Hola Mundo App"
    @echo "═══════════════════════════════════"
    @echo "📍 Servidor: http://localhost:8000"
    @echo "📍 MCP Endpoint: http://localhost:8000/mcp"
    @echo "📍 Docs API: http://localhost:8000/docs"

# Inicializar el proyecto (primera vez)
init:
    @echo "📦 Creando entorno virtual..."
    uv venv
    @echo "📥 Instalando dependencias..."
    uv sync
    @echo "📝 Configurando variables de entorno..."
    cp .env.example .env
    @echo "✅ Proyecto inicializado."

# Iniciar servidor de desarrollo
dev:
    @echo "🚀 Iniciando servidor de desarrollo..."
    uv run uvicorn src.helloworld_app.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar túnel ngrok
tunnel:
    @echo "🌍 Iniciando túnel ngrok..."
    @echo "⚠️  Copia la URL HTTPS y actualiza PUBLIC_URL en .env"
    ngrok http 8000
```

**Qué hace el comando `dev`:**
- `uv run`: Ejecuta el comando en el entorno virtual
- `uvicorn`: Servidor ASGI para ejecutar FastAPI
- `src.helloworld_app.main:app`: Ruta al objeto FastAPI (app en main.py)
- `--reload`: Reinicia automáticamente cuando cambias código
- `--host 0.0.0.0`: Permite conexiones desde cualquier interfaz de red
- `--port 8000`: Escucha en el puerto 8000

**✅ Validar ahora:**

```bash
just dev
```

**Salida esperada:**
```
🚀 Iniciando servidor de desarrollo...
INFO:     Will watch for changes in these directories: ['/ruta/a/tu/proyecto']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

**Verificar que el servidor funciona:**

En otra terminal, ejecuta:
```bash
curl http://localhost:8000/ | jq
```

Deberías ver:
```json
{
  "message": "Hola Mundo App está corriendo",
  "mcp_endpoint": "/mcp",
  "status": "ok"
}
```

Si ves este JSON, ¡tu servidor está corriendo correctamente! ✅

**Detener el servidor:** Presiona `Ctrl+C` en la terminal donde corre `just dev`.

🎓 **Aprendiste:**
- Cuándo agregar el comando `dev` (después de crear los archivos Python)
- Cómo uvicorn ejecuta aplicaciones ASGI/Starlette
- Cómo validar que el servidor está corriendo
- Cómo detener el servidor de desarrollo

---

## Parte 4: Probando Localmente

**⚠️ Prerequisitos:**
- ✅ Servidor corriendo con `just dev` (validado en sección 3.5)
- ✅ Terminal adicional abierta para ejecutar comandos `curl`

En esta parte vamos a probar directamente el **protocolo MCP** usando JSON-RPC 2.0.

### 4.1 Listar Herramientas MCP Disponibles

**Prerequisitos:**
- ✅ Servidor corriendo en terminal 1 con `just dev`
- ✅ Terminal 2 abierta para ejecutar curl

**⚠️ Nota sobre Server-Sent Events (SSE):**

El servidor MCP responde usando formato **Server-Sent Events (SSE)**, no JSON puro. La respuesta tiene este formato:
```
event: message
data: {json aquí}
```

Por eso necesitamos extraer la línea `data:` antes de pasarla a `jq`.

**Ejecutar la solicitud JSON-RPC:**

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }' 2>/dev/null | grep '^data:' | sed 's/^data: //' | jq
```

**Qué hace esto:**
- `POST http://localhost:8000/mcp`: Llamada al endpoint MCP
- `Content-Type: application/json`: Indica que enviamos JSON
- `Accept: application/json, text/event-stream`: Requerido por el servidor MCP
- `"method": "tools/list"`: Solicita lista de herramientas disponibles
- `"id": 1`: Identificador de la solicitud JSON-RPC
- `2>/dev/null`: Oculta el progreso de curl
- `grep '^data:'`: Filtra solo las líneas que empiezan con `data:`
- `sed 's/^data: //'`: Elimina el prefijo `data: ` dejando solo el JSON
- `| jq`: Formatea el JSON para que sea legible

**✅ Validar:**

Deberías ver un JSON que incluye la herramienta `say_hello` con su esquema completo:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "say_hello",
        "description": "Dice hola a alguien de manera amigable.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "name": {
              "description": "Nombre de la persona a saludar",
              "type": "string"
            },
            "emoji": {
              "default": true,
              "description": "¿Incluir emoji?",
              "type": "boolean"
            }
          },
          "required": ["name"]
        }
      }
    ]
  }
}
```

Si ves la herramienta `say_hello` listada, ¡el protocolo MCP funciona! ✅

### 4.2 Llamar la Herramienta MCP

**Prerequisitos:**
- ✅ Sección 4.1 completada (sabes que `say_hello` existe)

Ahora vamos a **ejecutar** la herramienta `say_hello`:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "say_hello",
      "arguments": {
        "input": {
          "name": "Claude",
          "emoji": true
        }
      }
    },
    "id": 2
  }' 2>/dev/null | grep '^data:' | sed 's/^data: //' | jq
```

**Qué hace esto:**
- `"method": "tools/call"`: Ejecuta una herramienta
- `"name": "say_hello"`: Nombre de la herramienta a ejecutar
- `"arguments"`: Parámetros de entrada envueltos en el objeto `input` (porque la función espera un parámetro `input: SayHelloInput`)
- `2>/dev/null | grep '^data:' | sed 's/^data: //'`: Extrae el JSON del formato SSE
- `| jq`: Formatea el JSON para que sea legible

**✅ Validar:**

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

Si ves `"¡Hola Claude! 👋"` en el resultado, ¡tu herramienta MCP funciona! ✅

### 4.3 Probar Diferentes Parámetros

**Prerequisitos:**
- ✅ Sección 4.2 completada (herramienta funciona con emoji)

Ahora probemos **sin emoji** para verificar que el parámetro `emoji` funciona:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "say_hello",
      "arguments": {
        "input": {
          "name": "María",
          "emoji": false
        }
      }
    },
    "id": 3
  }' 2>/dev/null | grep '^data:' | sed 's/^data: //' | jq
```

**Qué hace esto:**
- `"input"`: Objeto que contiene los parámetros (requerido porque la función espera `input: SayHelloInput`)
- `"name": "María"`: Diferente nombre
- `"emoji": false`: Sin emoji
- `2>/dev/null | grep '^data:' | sed 's/^data: //'`: Extrae el JSON del formato SSE

**✅ Validar:**

Deberías ver en el resultado: `"¡Hola María!"` (sin el emoji 👋)

Si el emoji no aparece, ¡los parámetros funcionan correctamente! ✅

🎓 **Aprendiste**:
- Cómo probar tu servidor MCP localmente con curl
- El formato de solicitudes JSON-RPC 2.0 (`method`, `params`, `id`)
- Cómo llamar herramientas MCP directamente sin ChatGPT
- **Que el servidor MCP responde en formato Server-Sent Events (SSE)**, no JSON puro
- **Cómo extraer JSON de SSE** usando `grep '^data:' | sed 's/^data: //'`
- Por qué necesitamos el header `Accept: application/json, text/event-stream`
- Cómo usar `jq` para formatear respuestas JSON

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

Primero, verifica el endpoint de salud:

```bash
# Usa tu URL de ngrok
curl https://abc123-45-67-89-10.ngrok-free.app/
```

Deberías ver el mensaje JSON con `"status": "ok"`. ✅

Luego, verifica que el endpoint MCP funciona a través de ngrok:

```bash
# Usa tu URL de ngrok
curl -X POST https://abc123-45-67-89-10.ngrok-free.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
  2>/dev/null | grep '^data:' | sed 's/^data: //' | jq
```

Deberías ver la lista de herramientas MCP (como `say_hello`). ✅

### 5.4 Conectar desde ChatGPT

Hay dos formas de conectar tu app a ChatGPT:

**Opción A: Desde ChatGPT directamente (Recomendado)**

1. Abre ChatGPT: https://chatgpt.com
2. Escribe en el chat:
   ```
   Conecta con mi servidor MCP en: https://tu-url-ngrok.ngrok-free.app/mcp
   ```
   ⚠️ **Importante**: Reemplaza `tu-url-ngrok.ngrok-free.app` con tu URL real de ngrok, y **no olvides el `/mcp` al final**

3. ChatGPT te pedirá confirmación. Acepta la conexión.
4. ¡Listo! ChatGPT ahora puede usar tus herramientas.

**Opción B: Desde OpenAI Platform**

1. Visita: https://platform.openai.com/playground/apps
2. Click en "Create App"
3. Llena el formulario:
   - **Name**: Hola Mundo App
   - **Description**: Tutorial básico de MCP
   - **MCP Server URL**: `https://tu-url-ngrok.ngrok-free.app/mcp` (⚠️ no olvides el `/mcp`)
4. Click en "Create"
5. La app estará disponible en ChatGPT

### 5.5 Probar en ChatGPT

Una vez conectado, en ChatGPT puedes decir:

**Ejemplo: Llamar la herramienta**
```
"Usa la app Hola Mundo para saludar a María"
```

ChatGPT debería:
1. Llamar a tu herramienta `say_hello`
2. Recibir `¡Hola María! 👋`
3. Mostrarte el resultado

**Otros ejemplos para probar:**
```
"Saluda a Juan sin emoji usando la app Hola Mundo"
"Usa say_hello para saludar a Ana"
```

> **💡 Nota**: Si quieres agregar widgets HTML interactivos a tu app, consulta el tutorial avanzado "Agregando Widgets a tu App MCP" (próximamente).

🎓 **Aprendiste**:
- Cómo exponer tu servidor local con ngrok
- Cómo registrar tu app en OpenAI Platform
- Cómo probar tu app en ChatGPT
- Cómo ChatGPT interpreta lenguaje natural para llamar tus herramientas

---

## 🎓 Resumen: ¿Qué Aprendiste?

### Conceptos

- ✅ **MCP (Model Context Protocol)**: Protocolo para que ChatGPT se comunique con aplicaciones
- ✅ **JSON-RPC 2.0**: Formato de mensajes que usa MCP
- ✅ **Herramientas MCP**: Funciones que ChatGPT puede llamar
- ✅ **Server-Sent Events (SSE)**: Formato de respuesta del servidor MCP
- ✅ **Pydantic**: Validación de datos de entrada para herramientas

### Habilidades Técnicas

- ✅ Configurar entorno reproducible con Nix
- ✅ Gestionar dependencias con `pyproject.toml` y `uv`
- ✅ Crear servidor MCP con FastMCP
- ✅ Definir herramientas con `@mcp.tool()`
- ✅ Validar entrada con modelos Pydantic
- ✅ Integrar MCP con Starlette
- ✅ Configurar CORS para permitir peticiones de ChatGPT
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
- Añade un parámetro para elegir el estilo de saludo (formal/informal)

### Nivel 2: Nueva Herramienta

- Añade una herramienta `farewell` que se despida
- Añade parámetros como `name`, `emoji`, `formal`
- Prueba ambas herramientas desde ChatGPT

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

### Logs: "Terminating session: None" - ¿Es un error?

**No es un error.** Cuando ves estos logs en tu servidor:

```
INFO: 127.0.0.1:62050 - "POST /mcp HTTP/1.1" 200 OK
Processing request of type ListToolsRequest
Terminating session: None
```

**Significado:**
- `200 OK`: La solicitud fue exitosa ✅
- `Processing request of type ListToolsRequest`: El servidor procesó una solicitud de lista de herramientas
- `Terminating session: None`: El servidor termina la "sesión" después de cada request

**¿Por qué aparece?**

Esto es el comportamiento normal del servidor MCP. El mensaje "Terminating session: None" simplemente indica que el servidor ha completado el procesamiento de la solicitud.

**Es normal y esperado** - ¡tu servidor está funcionando correctamente! 🎉

Estos logs son informativos y puedes ignorarlos con seguridad. No afectan la funcionalidad de tu aplicación.

### Error: "jq: parse error: Invalid numeric literal"

Este error ocurre cuando intentas usar `jq` directamente en la respuesta del servidor MCP sin extraer el JSON del formato SSE.

**Problema:**
```bash
# ❌ NO funciona (falta extracción SSE)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | jq
```

**Solución:**
```bash
# ✅ SÍ funciona (con extracción SSE)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
  2>/dev/null | grep '^data:' | sed 's/^data: //' | jq
```

**Explicación:** El servidor MCP responde en formato SSE (`event: message\ndata: {json}`), no JSON puro. Necesitas extraer la línea `data:` antes de parsear con `jq`.

### Error: "Not Acceptable: Client must accept both application/json and text/event-stream"

Este error ocurre cuando no incluyes el header `Accept` correcto en tus solicitudes al endpoint MCP.

**Problema:**
```bash
# ❌ NO funciona (falta header Accept)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

**Solución:**
```bash
# ✅ SÍ funciona (con header Accept)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
  2>/dev/null | grep '^data:' | sed 's/^data: //' | jq
```

**Explicación:** El servidor MCP requiere que el cliente indique que puede manejar tanto JSON como Server-Sent Events (SSE). Agrega el header `-H "Accept: application/json, text/event-stream"` a todas tus solicitudes MCP.

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
