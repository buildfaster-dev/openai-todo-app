# Tutorial: OpenAI ToDo App con Python y MCP

> **Tipo de documento**: Tutorial (Learning-oriented)
> **Objetivo**: Aprender a construir y extender la aplicación ToDo con OpenAI Apps SDK
> **Tiempo estimado**: 90-120 minutos
> **Nivel**: Principiante a Intermedio
> **Lenguaje**: Python 3.10+

## Introducción

En este tutorial, aprenderás a trabajar con la **OpenAI ToDo App**, una aplicación completa que integra el Model Context Protocol (MCP) con ChatGPT. Esta aplicación ya está construida, y la usarás para aprender:

- Cómo funciona una aplicación MCP real en Python
- La arquitectura de herramientas y widgets
- Cómo conectar tu app con ChatGPT
- Cómo extender la aplicación con nuevas funcionalidades

**Lo que aprenderás**: A entender, ejecutar y extender una aplicación Python MCP completa desde el setup hasta el despliegue.

## Prerrequisitos

### Software Requerido

- **Python 3.10 o superior**
- **Git** (para clonar el repositorio)
- **Editor de código** (VS Code recomendado)
- **Cuenta en ngrok** (gratuita) - [ngrok.com](https://ngrok.com)
- **Terminal** (bash, zsh, o similar)

### Conocimientos Previos Recomendados

- Python básico (funciones, clases, async/await)
- HTTP y APIs REST (conceptos básicos)
- JSON (formato de datos)

No te preocupes si no dominas estos temas - el tutorial explica cada paso.

---

## Parte 1: Setup y Exploración

### Paso 1: Clonar y Explorar el Proyecto

Si aún no has clonado el proyecto, hazlo ahora:

```bash
git clone <url-del-repositorio>
cd openai-todo-app
```

**Explora la estructura del proyecto**:

```bash
ls -la
```

Verás:
- `src/todo_app/` - Código fuente de la aplicación
- `docs/` - Documentación
- `tutorials/` - Este tutorial y otros
- `tests/` - Tests automatizados
- `pyproject.toml` - Dependencias Python
- `justfile` - Comandos útiles de desarrollo

**🎓 Aprendiste**: La estructura típica de un proyecto Python con OpenAI Apps SDK.

### Paso 2: Instalar uv (Gestor de Paquetes)

Este proyecto usa **uv**, un gestor de paquetes Python moderno y rápido.

```bash
# En Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verifica la instalación
uv --version
```

**¿Por qué uv?**
- 10-100x más rápido que pip
- Gestión automática de virtual environments
- Lock files para reproducibilidad
- Manejo mejor de dependencias

**🎓 Aprendiste**: Herramientas modernas del ecosistema Python.

### Paso 3: Inicializar el Proyecto

Usa el comando `just` para inicializar todo:

```bash
# Instalar just si no lo tienes
# En Linux/macOS con Homebrew:
brew install just

# O descarga desde: https://github.com/casey/just

# Inicializar el proyecto
just init
```

Este comando:
1. Crea un entorno virtual Python
2. Instala todas las dependencias
3. Configura el proyecto

**✅ Checkpoint**: Deberías ver el mensaje "✅ Project initialized!"

**🎓 Aprendiste**: Cómo usar `just` para automatizar tareas comunes de desarrollo.

### Paso 4: Explorar el Código

Abre el proyecto en tu editor. Vamos a entender cada archivo:

#### 4.1 Modelos de Datos (`src/todo_app/models.py`)

```python
class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TodoItem(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TodoStatus = TodoStatus.PENDING
    priority: TodoPriority = TodoPriority.MEDIUM
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    tags: list[str] = []
```

**¿Qué ves aquí?**
- `Enum`: Define valores válidos para status y priority
- `BaseModel` (Pydantic): Proporciona validación automática
- Type hints: Python moderno con tipos explícitos

**🎓 Aprendiste**: Cómo Pydantic valida datos automáticamente en Python.

#### 4.2 Almacenamiento (`src/todo_app/storage.py`)

```python
class TodoStorage:
    def __init__(self):
        self._todos: Dict[str, TodoItem] = {}
        self._initialize_sample_data()

    def create(self, todo_create: TodoCreate) -> TodoItem:
        todo_id = str(uuid.uuid4())
        todo = TodoItem(id=todo_id, ...)
        self._todos[todo_id] = todo
        return todo

    def list(self, status=None, tag=None) -> List[TodoItem]:
        todos = list(self._todos.values())
        # Filtrado y ordenamiento
        return todos
```

**¿Qué hace?**
- Almacenamiento en memoria (diccionario Python)
- CRUD completo: Create, Read, Update, Delete
- Filtrado por status y tags
- Datos de ejemplo precargados

**🎓 Aprendiste**: Patrón de almacenamiento simple pero funcional.

#### 4.3 Servidor MCP (`src/todo_app/mcp_server.py`)

Este es el corazón de la integración con ChatGPT. Exploraremos más en detalle en los siguientes pasos.

**✅ Checkpoint**: ¿Entiendes la estructura básica del proyecto?

---

## Parte 2: Ejecutar la Aplicación

### Paso 5: Iniciar el Servidor Local

Inicia el servidor de desarrollo:

```bash
just dev
```

Deberías ver:

```
🚀 Starting development server...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**¿Qué está pasando?**
- Uvicorn (servidor ASGI) ejecuta la aplicación FastAPI/Starlette
- El servidor escucha en el puerto 8000
- El modo `--reload` reinicia automáticamente al detectar cambios

**🎓 Aprendiste**: Cómo ejecutar un servidor ASGI Python.

### Paso 6: Probar el Endpoint MCP

En una **nueva terminal**, prueba el servidor:

```bash
# Lista todas las herramientas disponibles
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

Deberías ver una respuesta JSON con 7 herramientas:
- `show_todo_app`
- `show_todo_stats`
- `create_todo`
- `list_todos`
- `update_todo`
- `delete_todo`
- `get_todo`

**¿Qué acabas de hacer?**
- Enviaste una petición JSON-RPC 2.0
- El servidor MCP respondió con la lista de herramientas disponibles
- ChatGPT hace exactamente esto para descubrir capacidades

**🎓 Aprendiste**: Cómo el protocolo MCP usa JSON-RPC para comunicación.

### Paso 7: Probar Crear un Todo

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "create_todo",
      "arguments": {
        "title": "Mi primer todo desde curl",
        "description": "Probando la API MCP",
        "priority": "high"
      }
    }
  }'
```

Respuesta esperada:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {"type": "text", "text": "Created todo: Mi primer todo desde curl"}
    ],
    "structuredContent": {
      "todo": {
        "id": "abc-123-...",
        "title": "Mi primer todo desde curl",
        "description": "Probando la API MCP",
        "status": "pending",
        "priority": "high",
        ...
      }
    }
  }
}
```

**🎓 Aprendiste**: Cómo las herramientas MCP reciben argumentos y devuelven contenido estructurado.

**✅ Checkpoint**: ¿Puedes crear un todo exitosamente?

---

## Parte 3: Entender el Código MCP

### Paso 8: Anatomía de una Herramienta MCP

Abre `src/todo_app/mcp_server.py` y busca la función `_list_tools()`:

```python
@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List all available tools"""
    return [
        types.Tool(
            name="create_todo",
            title="Create Todo",
            description="Create a new todo item with title, description, and priority",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the todo item"},
                    "description": {"type": "string", "description": "A detailed description"},
                    "priority": {"type": "string", "description": "Priority: low, medium, or high"},
                },
                "required": ["title"],
                "additionalProperties": False,
            },
            annotations={
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": False,
            },
        ),
        # ... más herramientas
    ]
```

**Anatomía de una Tool**:

1. **name**: Identificador único (`create_todo`)
2. **title**: Nombre amigable para humanos
3. **description**: Lo que hace la herramienta (ChatGPT usa esto para decidir cuándo llamarla)
4. **inputSchema**: Schema JSON que define qué parámetros acepta
5. **annotations**: Hints sobre el comportamiento:
   - `destructiveHint`: ¿Elimina o modifica datos?
   - `openWorldHint`: ¿Accede a servicios externos?
   - `readOnlyHint`: ¿Solo lectura?

**🎓 Aprendiste**: La estructura de una herramienta MCP en Python.

### Paso 9: Implementación de una Herramienta

Ahora busca `_call_tool_request()` en el mismo archivo:

```python
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    if tool_name == "create_todo":
        # 1. Validar entrada con Pydantic
        payload = CreateTodoInput.model_validate(arguments)

        # 2. Crear objeto con el modelo de negocio
        todo_create = TodoCreate(
            title=payload.title,
            description=payload.description,
            priority=payload.priority
        )

        # 3. Guardar en storage
        todo = storage.create(todo_create)

        # 4. Devolver resultado estructurado
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Created todo: {todo.title}",
                    )
                ],
                structuredContent={"todo": todo.model_dump(mode='json')},
            )
        )
```

**Flujo de ejecución**:
1. **Validación**: Pydantic verifica que los argumentos son correctos
2. **Lógica de negocio**: Crea el todo en el storage
3. **Respuesta**: Devuelve texto legible + datos estructurados

**¿Por qué dos tipos de contenido?**
- `content`: Lo que ChatGPT muestra al usuario
- `structuredContent`: Datos que ChatGPT puede usar para operaciones posteriores

**🎓 Aprendiste**: El patrón de implementación de herramientas MCP en Python.

---

## Parte 4: Widgets e Interfaz Visual

### Paso 10: Entender los Widgets

Los widgets son interfaces HTML que se muestran en ChatGPT. Busca la función `_get_todo_list_html()`:

```python
def _get_todo_list_html() -> str:
    """Generate interactive HTML for todo list widget"""
    todos = storage.list()
    todos_data = [todo.model_dump(mode='json') for todo in todos]
    stats = storage.get_stats()

    import json
    todos_json = json.dumps(todos_data)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        /* CSS inline */
        body {{ font-family: -apple-system, sans-serif; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
    </style>
</head>
<body>
    <div class="header">📝 Your Todo App</div>

    <script>
        let todos = {todos_json};
        const API_BASE = '{PUBLIC_URL}/api';

        function renderTodos() {{
            // Lógica de renderizado
        }}
    </script>
</body>
</html>"""
```

**Características clave**:
1. **HTML autocontenido**: Todo el CSS y JS inline
2. **Datos inyectados**: `{todos_json}` se inyecta desde Python
3. **PUBLIC_URL**: Configurado para que los botones funcionen
4. **Interactivo**: JavaScript hace peticiones a la API REST

**🎓 Aprendiste**: Cómo los widgets combinan Python (backend) con HTML/JS (frontend).

### Paso 11: Asociar Widget con Herramienta

Busca cómo `show_todo_app` define su widget:

```python
types.Tool(
    name="show_todo_app",
    title="Show Todo App",
    description="Open the full todo app interface",
    inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
    _meta={
        "openai/outputTemplate": "ui://widget/todo-app.html",
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    },
)
```

Y cómo se registra el recurso:

```python
@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name="Todo App Widget",
            title="Todo App",
            uri="ui://widget/todo-app.html",
            description="Interactive todo app",
            mimeType="text/html+skybridge",
        )
    ]
```

**Flujo completo**:
1. ChatGPT llama `show_todo_app`
2. Ve el `_meta` con `openai/outputTemplate`
3. Solicita el recurso `ui://widget/todo-app.html`
4. El servidor genera HTML dinámicamente con `_get_todo_list_html()`
5. ChatGPT renderiza el HTML en un iframe

**🎓 Aprendiste**: La arquitectura de widgets en MCP.

---

## Parte 5: Configuración y Despliegue

### Paso 12: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Edita `.env`:

```bash
# .env
HOST=0.0.0.0
PORT=8000
DEBUG=true
PUBLIC_URL=http://localhost:8000
```

**¿Por qué PUBLIC_URL?**
- Los widgets se renderizan en `chat.openai.com`
- Los botones necesitan saber dónde está tu API
- En desarrollo: `http://localhost:8000`
- En producción: Tu URL pública de ngrok

**🎓 Aprendiste**: Configuración de entorno en aplicaciones Python.

### Paso 13: Exponer con ngrok

Para que ChatGPT pueda comunicarse con tu aplicación local:

```bash
# En una nueva terminal
just tunnel
```

O manualmente:

```bash
ngrok http 8000
```

Verás algo como:

```
Session Status                online
Account                       tu-cuenta (Plan: Free)
Forwarding                    https://abc123.ngrok-free.dev -> http://localhost:8000
```

**Copia la URL HTTPS** (ejemplo: `https://abc123.ngrok-free.dev`)

**Actualiza tu `.env`**:

```bash
PUBLIC_URL=https://abc123.ngrok-free.dev
```

**Reinicia el servidor** (Ctrl+C y luego `just dev`)

**✅ Checkpoint**: ¿Tienes ngrok corriendo y la URL copiada?

**🎓 Aprendiste**: Cómo exponer servicios locales a internet de forma segura.

### Paso 14: Configurar en OpenAI Platform

1. Ve a [platform.openai.com/apps](https://platform.openai.com/apps)

2. Haz clic en **"Create new app"**

3. Configura:
   - **Name**: OpenAI ToDo App
   - **Description**: Manage your todos through ChatGPT
   - **MCP Server Endpoint**: `https://tu-ngrok-url.ngrok-free.dev/mcp`
   - ⚠️ **Importante**: Incluye `/mcp` al final

4. **Guarda** la configuración

5. **Publica** la app

**🎓 Aprendiste**: Cómo conectar tu servidor MCP con la plataforma OpenAI.

### Paso 15: Probar en ChatGPT

1. Ve a [chat.openai.com](https://chat.openai.com)

2. Busca tu app en el selector de apps (ícono de plugins)

3. Activa "OpenAI ToDo App"

4. **Prueba estos comandos**:

```
"Show me my todos"
```

Deberías ver el widget interactivo con tus todos.

```
"Create a todo for buying groceries with high priority"
```

ChatGPT usará la herramienta `create_todo`.

```
"What are my statistics?"
```

Verás el widget de estadísticas.

```
"List only my pending todos"
```

ChatGPT filtrará por status.

**🎉 ¡Felicidades!** Tu aplicación está funcionando con ChatGPT.

**✅ Checkpoint**: ¿Puedes ver y usar tu app en ChatGPT?

---

## Parte 6: Extender la Aplicación

Ahora que entiendes cómo funciona, vamos a agregar una nueva funcionalidad.

### Paso 16: Agregar una Nueva Herramienta - "Search Todos"

Vamos a implementar una herramienta para buscar todos por texto.

#### 16.1 Agregar el Schema de Entrada

En `src/todo_app/mcp_server.py`, después de las otras clases de input, agrega:

```python
class SearchTodosInput(BaseModel):
    """Schema for searching todos"""
    query: str = Field(..., description="Text to search in title and description")

    model_config = ConfigDict(extra="forbid")
```

#### 16.2 Agregar Método de Búsqueda al Storage

En `src/todo_app/storage.py`, agrega este método a la clase `TodoStorage`:

```python
def search(self, query: str) -> List[TodoItem]:
    """Search todos by text in title or description"""
    query_lower = query.lower()
    return [
        todo for todo in self._todos.values()
        if query_lower in todo.title.lower() or
           (todo.description and query_lower in todo.description.lower())
    ]
```

#### 16.3 Registrar la Herramienta

En `_list_tools()`, agrega:

```python
types.Tool(
    name="search_todos",
    title="Search Todos",
    description="Search for todos by text in title or description",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Text to search for"},
        },
        "required": ["query"],
        "additionalProperties": False,
    },
    annotations={
        "destructiveHint": False,
        "openWorldHint": False,
        "readOnlyHint": True,
    },
),
```

#### 16.4 Implementar el Handler

En `_call_tool_request()`, agrega este caso:

```python
elif tool_name == "search_todos":
    payload = SearchTodosInput.model_validate(arguments)
    todos = storage.search(payload.query)

    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Found {len(todos)} todo(s) matching '{payload.query}'",
                )
            ],
            structuredContent={
                "todos": [todo.model_dump(mode='json') for todo in todos],
                "query": payload.query,
                "count": len(todos),
            },
        )
    )
```

#### 16.5 Probar la Nueva Herramienta

El servidor en modo `--reload` debería reiniciarse automáticamente. Si no:

```bash
# Reinicia el servidor
# Ctrl+C y luego:
just dev
```

Prueba con curl:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "search_todos",
      "arguments": {
        "query": "development"
      }
    }
  }'
```

**En ChatGPT**:

```
"Search for todos about development"
```

ChatGPT debería usar tu nueva herramienta `search_todos`.

**🎉 ¡Lo lograste!** Agregaste una nueva funcionalidad completa.

**🎓 Aprendiste**: El ciclo completo de desarrollo: schema → storage → tool → handler → test.

---

## Parte 7: Testing y Debugging

### Paso 17: Escribir un Test

Crea `tests/test_search.py`:

```python
"""Tests for search functionality"""

import pytest
from src.todo_app.storage import TodoStorage
from src.todo_app.models import TodoCreate, TodoPriority


def test_search_todos():
    """Test searching todos by text"""
    storage = TodoStorage()

    # Create test todos
    storage.create(TodoCreate(
        title="Buy milk",
        description="From the grocery store",
        priority=TodoPriority.HIGH
    ))

    storage.create(TodoCreate(
        title="Call dentist",
        description="Schedule appointment",
        priority=TodoPriority.MEDIUM
    ))

    # Search by title
    results = storage.search("milk")
    assert len(results) == 1
    assert results[0].title == "Buy milk"

    # Search by description
    results = storage.search("appointment")
    assert len(results) == 1
    assert results[0].title == "Call dentist"

    # Search not found
    results = storage.search("xyz123")
    assert len(results) == 0


def test_search_case_insensitive():
    """Test that search is case insensitive"""
    storage = TodoStorage()

    storage.create(TodoCreate(
        title="Python Tutorial",
        description="Learn Python basics",
        priority=TodoPriority.LOW
    ))

    # Should find regardless of case
    assert len(storage.search("python")) == 1
    assert len(storage.search("PYTHON")) == 1
    assert len(storage.search("PyThOn")) == 1
```

Ejecuta los tests:

```bash
just test
```

Deberías ver:

```
🧪 Running tests...
tests/test_search.py::test_search_todos PASSED
tests/test_search.py::test_search_case_insensitive PASSED
```

**🎓 Aprendiste**: Cómo escribir tests con pytest para tu aplicación Python.

### Paso 18: Debugging con Logs

Agrega logging a tu código. En `src/todo_app/mcp_server.py`:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    logger.info(f"Tool called: {tool_name}")
    logger.debug(f"Arguments: {arguments}")

    # ... resto del código
```

Ahora verás logs en la consola cuando se llamen herramientas:

```
INFO:     Tool called: create_todo
INFO:     Tool called: search_todos
```

**🎓 Aprendiste**: Cómo usar logging para debugging en Python.

---

## Parte 8: Mejores Prácticas y Siguientes Pasos

### Paso 19: Mejores Prácticas Aprendidas

**1. Type Hints Siempre**
```python
# ✅ BIEN
def search(self, query: str) -> List[TodoItem]:
    ...

# ❌ MAL
def search(self, query):
    ...
```

**2. Validación con Pydantic**
```python
# ✅ BIEN - Pydantic valida automáticamente
payload = SearchTodosInput.model_validate(arguments)

# ❌ MAL - Sin validación
query = arguments["query"]
```

**3. Manejo de Errores**
```python
# ✅ BIEN
try:
    payload = SearchTodosInput.model_validate(arguments)
    # ...
except ValidationError as exc:
    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Error: {exc}")],
            isError=True,
        )
    )
```

**4. Descripciones Claras**
```python
# ✅ BIEN
description="Search for todos by text in title or description"

# ❌ MAL
description="Search"
```

**5. Structured Content**
```python
# ✅ BIEN - Datos estructurados + texto legible
return types.ServerResult(
    types.CallToolResult(
        content=[types.TextContent(type="text", text="Found 3 todos")],
        structuredContent={"todos": [...], "count": 3}
    )
)
```

**🎓 Aprendiste**: Patrones y prácticas para código Python limpio y robusto.

### Paso 20: Siguientes Pasos

**Mejoras que puedes hacer**:

1. **Agregar Persistencia**
   - Implementar SQLite o PostgreSQL
   - Ver `docs/GUIDE.md` sección "Cómo usar PostgreSQL"

2. **Agregar Autenticación**
   - Implementar JWT tokens
   - Proteger endpoints con usuarios

3. **Agregar Notificaciones**
   - Emails cuando un todo vence
   - Webhooks para integraciones

4. **Mejorar el Widget**
   - Drag & drop para reordenar
   - Editor markdown para descripciones
   - Temas dark/light

5. **Agregar Tests E2E**
   - Tests de integración completos
   - Tests del protocolo MCP

6. **Deploy a Producción**
   - Railway, Render, o Fly.io
   - Configurar dominio personalizado
   - SSL/TLS automático

**Recursos adicionales**:
- `docs/GUIDE.md` - Guía de referencia para tareas específicas
- `docs/EXPLANATION.md` - Conceptos profundos y arquitectura
- `OPENAI_APPS_SDK.md` - Setup y configuración detallada

---

## Resumen

¡Felicidades por completar el tutorial! Has aprendido:

### Conceptos de MCP
- ✅ Protocolo JSON-RPC 2.0
- ✅ Herramientas y su estructura
- ✅ Recursos y widgets HTML
- ✅ Contenido estructurado

### Python y FastAPI
- ✅ Pydantic para validación
- ✅ Type hints y código tipado
- ✅ Async/await y ASGI
- ✅ Testing con pytest

### Desarrollo de Apps
- ✅ Setup con uv y just
- ✅ Estructura de proyecto
- ✅ Variables de entorno
- ✅ Debugging y logging

### Integración con OpenAI
- ✅ Configurar ngrok
- ✅ Conectar con OpenAI Platform
- ✅ Probar en ChatGPT
- ✅ Widgets interactivos

### Extensión
- ✅ Agregar nuevas herramientas
- ✅ Escribir tests
- ✅ Mejores prácticas

---

## Troubleshooting Común

### El servidor no inicia

**Error**: `ModuleNotFoundError`

**Solución**:
```bash
just install
source .venv/bin/activate
```

### ngrok muestra 502 Bad Gateway

**Causa**: El servidor local no está corriendo

**Solución**:
```bash
# En una terminal:
just dev

# En otra terminal:
just tunnel
```

### ChatGPT no encuentra las herramientas

**Solución**:
1. Verifica que ngrok está corriendo
2. Confirma la URL en OpenAI Platform incluye `/mcp`
3. Inicia una nueva conversación en ChatGPT

### Los botones del widget no funcionan

**Causa**: `PUBLIC_URL` no configurado correctamente

**Solución**:
```bash
# En .env
PUBLIC_URL=https://tu-url-ngrok.ngrok-free.dev

# Reinicia el servidor
just dev
```

---

## Ayuda y Soporte

- **Documentación**: Ver `docs/` para guías detalladas
- **Issues**: Reportar problemas en el repositorio
- **Ejemplos**: [OpenAI Apps SDK Examples](https://github.com/openai/openai-apps-sdk-examples)

---

**¡Feliz construcción!** 🚀

**Próximos tutoriales**:
- `tutorials/notes-app-tutorial.md` - Construir una app desde cero
- Próximamente: Tutorial de deploy a producción
- Próximamente: Tutorial de autenticación
