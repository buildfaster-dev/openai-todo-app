# Guía de Referencia: OpenAI Apps SDK con Python

> **Tipo de documento**: How-to Guide (Task-oriented)
> **Objetivo**: Resolver problemas específicos y realizar tareas concretas usando Python
> **Lenguaje**: Python 3.10+
> **Audiencia**: Desarrolladores Python que ya tienen conocimientos básicos del SDK

## Tabla de Contenidos

- [Configuración y Setup](#configuración-y-setup)
- [Herramientas MCP](#herramientas-mcp)
- [Widgets e Interfaz](#widgets-e-interfaz)
- [Integración con OpenAI](#integración-con-openai)
- [Testing y Debugging](#testing-y-debugging)
- [Despliegue y Producción](#despliegue-y-producción)
- [Troubleshooting](#troubleshooting)

---

## Configuración y Setup

### Cómo configurar variables de entorno

**Problema**: Necesitas configurar variables de entorno para tu aplicación.

**Solución**:

1. Crea un archivo `.env` en la raíz de tu proyecto:

```bash
# .env
PUBLIC_URL=https://tu-url-ngrok.ngrok-free.dev
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

2. Carga las variables en tu código:

```python
from dotenv import load_dotenv
import os

load_dotenv()

PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")
PORT = int(os.getenv("PORT", "8000"))
```

3. Nunca commitas el archivo `.env` al repositorio:

```bash
echo ".env" >> .gitignore
```

### Cómo cambiar el puerto del servidor

**Problema**: El puerto 8000 ya está en uso.

**Solución**:

Opción 1 - Usando variable de entorno:

```bash
PORT=8080 uv run uvicorn src.notes_app.main:app --reload
```

Opción 2 - Especificando en el comando:

```bash
uv run uvicorn src.notes_app.main:app --reload --port 8080
```

Opción 3 - Modificando el código en `main.py`:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.notes_app.main:app", host="0.0.0.0", port=8080, reload=True)
```

### Cómo usar uv para gestión de dependencias Python

**Problema**: Quieres gestionar dependencias Python de forma rápida y confiable.

**Solución**:

1. Instala uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Crea un proyecto nuevo:

```bash
uv init mi-proyecto
cd mi-proyecto
```

3. Agrega dependencias:

```bash
# Dependencias de producción
uv add fastapi uvicorn pydantic "mcp[fastapi]"

# Dependencias de desarrollo
uv add --dev pytest pytest-asyncio httpx
```

4. Sincroniza el entorno:

```bash
uv sync
```

5. Ejecuta comandos en el entorno:

```bash
uv run python mi_script.py
uv run pytest
```

**¿Por qué uv?**
- 10-100x más rápido que pip
- Lock files automáticos (uv.lock)
- Gestión automática de virtual environments
- Compatible con pyproject.toml estándar

---

## Herramientas MCP

### Cómo agregar una nueva herramienta

**Problema**: Quieres agregar una nueva funcionalidad que ChatGPT pueda usar.

**Solución**:

1. Define el schema de entrada:

```python
class MyToolInput(BaseModel):
    """Schema for my custom tool"""
    param1: str = Field(..., description="Description of param1")
    param2: Optional[int] = Field(None, description="Optional param2")

    model_config = ConfigDict(extra="forbid")
```

2. Agrega la herramienta en `list_tools()`:

```python
@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    return [
        # ... otras herramientas
        types.Tool(
            name="my_custom_tool",
            title="My Custom Tool",
            description="Does something useful",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Description of param1"},
                    "param2": {"type": "integer", "description": "Optional param2"},
                },
                "required": ["param1"],
                "additionalProperties": False,
            },
            annotations={
                "destructiveHint": False,  # True si elimina/modifica datos
                "openWorldHint": False,    # True si accede a servicios externos
                "readOnlyHint": True,      # True si solo lee, no modifica
            },
        ),
    ]
```

3. Implementa el handler en `_call_tool_request()`:

```python
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    if tool_name == "my_custom_tool":
        payload = MyToolInput.model_validate(arguments)

        # Tu lógica aquí
        result = do_something(payload.param1, payload.param2)

        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Result: {result}",
                    )
                ],
                structuredContent={"data": result},
            )
        )
```

### Cómo manejar errores en herramientas

**Problema**: Quieres proporcionar mensajes de error claros cuando algo falla.

**Solución**:

```python
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    try:
        if tool_name == "my_tool":
            payload = MyToolInput.model_validate(arguments)

            # Validación de negocio
            if not is_valid(payload.param1):
                return types.ServerResult(
                    types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="❌ Invalid input: param1 must be...",
                            )
                        ],
                        isError=True,
                    )
                )

            # Lógica normal
            result = process(payload)
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"✅ Success: {result}",
                        )
                    ],
                )
            )

    except ValidationError as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"❌ Validation error: {exc.errors()}",
                    )
                ],
                isError=True,
            )
        )
    except Exception as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"❌ Unexpected error: {str(exc)}",
                    )
                ],
                isError=True,
            )
        )
```

### Cómo agregar parámetros opcionales

**Problema**: Quieres que algunos parámetros sean opcionales con valores por defecto.

**Solución**:

```python
class MyToolInput(BaseModel):
    required_param: str = Field(..., description="This is required")
    optional_param: Optional[str] = Field(None, description="This is optional")
    optional_with_default: int = Field(10, description="Optional with default value")

# En el inputSchema:
inputSchema={
    "type": "object",
    "properties": {
        "required_param": {"type": "string", "description": "This is required"},
        "optional_param": {"type": "string", "description": "This is optional"},
        "optional_with_default": {
            "type": "integer",
            "description": "Optional with default value",
            "default": 10
        },
    },
    "required": ["required_param"],  # Solo los requeridos
    "additionalProperties": False,
}
```

---

## Widgets e Interfaz

### Cómo crear un widget básico

**Problema**: Quieres mostrar una interfaz visual en ChatGPT.

**Solución**:

1. Define la función que genera el HTML:

```python
def _get_my_widget_html() -> str:
    """Generate HTML for my widget"""
    data = get_my_data()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Widget</title>
    <style>
        body {{
            font-family: -apple-system, sans-serif;
            margin: 0;
            padding: 16px;
            background: white;
        }}
        .container {{
            max-width: 600px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>My Widget Title</h2>
        <p>Data: {data}</p>
    </div>
</body>
</html>"""
```

2. Registra el recurso:

```python
WIDGET_URI = "ui://widget/my-widget.html"
MIME_TYPE = "text/html+skybridge"

@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name="My Widget",
            title="My Widget",
            uri=WIDGET_URI,
            description="My custom widget",
            mimeType=MIME_TYPE,
        )
    ]
```

3. Implementa el handler:

```python
async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    if str(req.params.uri) == WIDGET_URI:
        html = _get_my_widget_html()
        contents = [
            types.TextResourceContents(
                uri=WIDGET_URI,
                mimeType=MIME_TYPE,
                text=html,
            )
        ]
        return types.ServerResult(types.ReadResourceResult(contents=contents))

    return types.ServerResult(
        types.ReadResourceResult(
            contents=[],
            _meta={"error": f"Unknown resource: {req.params.uri}"},
        )
    )

mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource
```

4. Asocia el widget a una herramienta:

```python
types.Tool(
    name="show_my_widget",
    title="Show My Widget",
    description="Display my custom widget",
    inputSchema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    _meta={
        "openai/outputTemplate": WIDGET_URI,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    },
)
```

### Cómo hacer un widget interactivo

**Problema**: Quieres que tu widget tenga botones y formularios funcionales.

**Solución**:

1. **Configura PUBLIC_URL** en `.env`:

```bash
PUBLIC_URL=https://tu-url-ngrok.ngrok-free.dev
```

2. **Carga PUBLIC_URL** en tu código:

```python
import os
from dotenv import load_dotenv

load_dotenv()
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")
```

3. **Crea endpoints REST API** en `main.py`:

```python
from starlette.routing import Route
from starlette.responses import JSONResponse

async def create_item_endpoint(request: Request) -> JSONResponse:
    data = await request.json()
    # Procesar datos
    return JSONResponse({"success": True, "id": "123"})

# Agregar rutas al app
app.routes.extend([
    Route("/api/items", create_item_endpoint, methods=["POST"]),
])
```

4. **Usa PUBLIC_URL en tu widget HTML**:

```python
def _get_interactive_widget_html() -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        .btn {{
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }}
        .btn:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <button class="btn" onclick="createItem()">Create Item</button>

    <script>
        const API_BASE = '{PUBLIC_URL}/api';

        async function createItem() {{
            try {{
                const response = await fetch(`${{API_BASE}}/items`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ name: 'New Item' }})
                }});

                if (response.ok) {{
                    const data = await response.json();
                    alert('Item created: ' + data.id);
                }} else {{
                    alert('Error creating item');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                alert('Network error');
            }}
        }}
    </script>
</body>
</html>"""
```

**Nota importante**: Los widgets se renderizan en el dominio de OpenAI, por eso necesitas `PUBLIC_URL` - no puedes usar `window.location.origin`.

### Cómo pasar datos dinámicos a un widget

**Problema**: Quieres que el widget muestre datos actuales cada vez que se carga.

**Solución**:

1. Genera los datos en el momento de la petición:

```python
def _get_dynamic_widget_html() -> str:
    # Obtener datos frescos
    items = storage.list()
    stats = storage.get_stats()

    # Serializar para JavaScript
    import json
    items_json = json.dumps([item.model_dump(mode='json') for item in items])

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <div id="stats">Total: {stats['total']}</div>
    <div id="items"></div>

    <script>
        const items = {items_json};

        function renderItems() {{
            const container = document.getElementById('items');
            container.innerHTML = items.map(item => `
                <div>${{item.title}}</div>
            `).join('');
        }}

        renderItems();
    </script>
</body>
</html>"""
```

2. Los datos se generan cada vez que ChatGPT llama a `resources/read`.

### Cómo estilizar un widget profesionalmente

**Problema**: Quieres que tu widget se vea profesional.

**Solución** - Usa CSS inline con buenas prácticas:

```python
def _get_styled_widget_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 16px;
            background: white;
            color: #111827;
        }

        .card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            transition: box-shadow 0.2s;
        }

        .card:hover {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .btn {
            padding: 8px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn:active {
            transform: translateY(0);
        }
    </style>
</head>
<body>
    <div class="card">
        <h3>Beautiful Card</h3>
        <p>This looks professional!</p>
        <button class="btn">Click Me</button>
    </div>
</body>
</html>"""
```

**Tips de diseño**:
- Usa la fuente del sistema (`-apple-system, sans-serif`)
- Colores neutros para fondo (#f9fafb, #ffffff)
- Bordes sutiles (#e5e7eb)
- Gradientes para destacar (#667eea → #764ba2)
- Transiciones suaves (0.2s)
- Border-radius para esquinas redondeadas (6-8px)

---

## Integración con OpenAI

### Cómo configurar tu app en OpenAI Platform

**Problema**: Necesitas conectar tu servidor MCP con OpenAI.

**Solución**:

1. Ve a [platform.openai.com/apps](https://platform.openai.com/apps)

2. Haz clic en "Create new app"

3. Configura:
   - **Name**: Nombre descriptivo de tu app
   - **Description**: Qué hace tu aplicación
   - **MCP Server Endpoint**: `https://tu-ngrok-url.ngrok-free.dev/mcp`
   - **Headers**: Asegúrate de que se envíen:
     - `Content-Type: application/json`
     - `Accept: application/json, text/event-stream`

4. Guarda y publica la app

5. Ve a ChatGPT y activa tu app desde el selector de apps

### Cómo actualizar tu app después de cambios

**Problema**: Hiciste cambios en el código y ChatGPT no los ve.

**Solución**:

1. **Reinicia el servidor local**:
```bash
# Ctrl+C para detener, luego:
uv run uvicorn src.notes_app.main:app --reload --port 8000
```

2. **No necesitas actualizar nada en OpenAI Platform** - los cambios se reflejan inmediatamente

3. **En ChatGPT**, empieza una conversación nueva para que recargue las herramientas

4. **Si cambiaste la URL de ngrok**:
   - Actualiza el endpoint en OpenAI Platform
   - Actualiza `PUBLIC_URL` en tu `.env`
   - Reinicia el servidor

### Cómo probar tu app sin ChatGPT

**Problema**: Quieres probar tu servidor MCP localmente.

**Solución**:

Usa curl para simular peticiones MCP:

```bash
# Listar herramientas
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'

# Llamar herramienta
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "create_note",
      "arguments": {
        "title": "Test",
        "content": "Testing"
      }
    }
  }'

# Leer widget
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "resources/read",
    "params": {
      "uri": "ui://widget/notes-list.html"
    }
  }'
```

---

## Testing y Debugging

### Cómo agregar logging

**Problema**: Quieres ver qué está pasando en tu servidor.

**Solución**:

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Usar en tu código
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    logger.info(f"Tool called: {tool_name}")
    logger.debug(f"Arguments: {arguments}")

    try:
        # Tu lógica
        result = process(arguments)
        logger.info(f"Tool {tool_name} succeeded")
        return result
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}", exc_info=True)
        raise
```

### Cómo escribir tests unitarios

**Problema**: Quieres asegurar que tu código funciona correctamente.

**Solución**:

1. Instala pytest:

```bash
uv add --dev pytest pytest-asyncio
```

2. Crea `tests/test_storage.py`:

```python
import pytest
from src.notes_app.storage import NotesStorage
from src.notes_app.models import NoteCreate

def test_create_note():
    storage = NotesStorage()
    note_create = NoteCreate(title="Test", content="Test content")
    note = storage.create(note_create)

    assert note.id is not None
    assert note.title == "Test"
    assert note.content == "Test content"

def test_list_notes():
    storage = NotesStorage()
    storage.create(NoteCreate(title="Note 1", content="Content 1"))
    storage.create(NoteCreate(title="Note 2", content="Content 2"))

    notes = storage.list()
    assert len(notes) == 2

def test_delete_note():
    storage = NotesStorage()
    note = storage.create(NoteCreate(title="Test", content="Test"))

    result = storage.delete(note.id)
    assert result is True

    result = storage.delete("non-existent")
    assert result is False
```

3. Ejecuta los tests:

```bash
uv run pytest
```

### Cómo debuggear problemas de CORS

**Problema**: Ves errores de CORS en la consola del navegador.

**Solución**:

1. Verifica que CORS está configurado:

```python
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Verifica en las herramientas de desarrollador:
   - Abre la consola (F12) en ChatGPT
   - Busca errores que digan "CORS"
   - Verifica que la petición incluye los headers correctos

3. Prueba manualmente con curl:

```bash
curl -X OPTIONS http://localhost:8000/api/items \
  -H "Origin: https://chat.openai.com" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

Deberías ver headers de respuesta como:
- `access-control-allow-origin: *`
- `access-control-allow-methods: *`

---

## Despliegue y Producción

### Cómo desplegar en Railway

**Problema**: Quieres que tu app esté disponible 24/7 sin ngrok.

**Solución**:

1. Crea una cuenta en [railway.app](https://railway.app)

2. Crea un archivo `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uv run uvicorn src.notes_app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

3. Agrega un `Procfile`:

```
web: uv run uvicorn src.notes_app.main:app --host 0.0.0.0 --port $PORT
```

4. Sube tu código:

```bash
git init
git add .
git commit -m "Initial commit"
```

5. En Railway:
   - "New Project" → "Deploy from GitHub repo"
   - Selecciona tu repositorio
   - Railway detectará Python y desplegará automáticamente

6. Configura variables de entorno en Railway:
   - `PUBLIC_URL`: La URL que Railway te asigna
   - Cualquier otra variable necesaria

7. Actualiza OpenAI Platform con la nueva URL de Railway

### Cómo usar PostgreSQL en lugar de almacenamiento en memoria

**Problema**: Quieres persistir datos en una base de datos real.

**Solución**:

1. Instala dependencias:

```bash
uv add sqlalchemy psycopg2-binary alembic
```

2. Crea `src/notes_app/database.py`:

```python
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NoteDB(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)
```

3. Actualiza `storage.py` para usar SQLAlchemy:

```python
from sqlalchemy.orm import Session
from .database import SessionLocal, NoteDB
from .models import Note, NoteCreate

class NotesStorage:
    def create(self, note_create: NoteCreate) -> Note:
        db = SessionLocal()
        try:
            note_db = NoteDB(
                id=str(uuid4()),
                title=note_create.title,
                content=note_create.content,
                created_at=datetime.utcnow()
            )
            db.add(note_db)
            db.commit()
            db.refresh(note_db)

            return Note(
                id=note_db.id,
                title=note_db.title,
                content=note_db.content,
                created_at=note_db.created_at
            )
        finally:
            db.close()

    def list(self) -> List[Note]:
        db = SessionLocal()
        try:
            notes_db = db.query(NoteDB).all()
            return [
                Note(
                    id=note.id,
                    title=note.title,
                    content=note.content,
                    created_at=note.created_at
                )
                for note in notes_db
            ]
        finally:
            db.close()
```

---

## Troubleshooting

### El widget no se muestra en ChatGPT

**Síntomas**: ChatGPT responde pero no muestra el widget.

**Diagnóstico**:

1. ✅ Verifica que la herramienta tiene `_meta` con `openai/outputTemplate`:

```python
_meta={
    "openai/outputTemplate": "ui://widget/my-widget.html",
    "openai/widgetAccessible": True,
    "openai/resultCanProduceWidget": True,
}
```

2. ✅ Verifica que el recurso está registrado en `list_resources()`

3. ✅ Verifica que `read_resource()` devuelve HTML con MIME type correcto:

```python
mimeType="text/html+skybridge"
```

4. ✅ Prueba el endpoint directamente:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "resources/read",
    "params": {"uri": "ui://widget/my-widget.html"}
  }'
```

Deberías ver el HTML en la respuesta.

### Los botones del widget no funcionan

**Síntomas**: El widget se muestra pero los botones no hacen nada.

**Diagnóstico**:

1. ✅ Verifica que `PUBLIC_URL` está configurado en `.env`

2. ✅ Verifica que reiniciaste el servidor después de configurar `PUBLIC_URL`

3. ✅ Abre la consola del navegador (F12) en ChatGPT y busca errores

4. ✅ Verifica que CORS está habilitado correctamente

5. ✅ Prueba el endpoint REST API directamente:

```bash
curl -X POST https://tu-ngrok-url/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'
```

### Error "Not Acceptable" (406)

**Síntomas**: Las peticiones a `/mcp` devuelven 406.

**Causa**: Faltan headers de Accept.

**Solución**:

Asegúrate de enviar ambos headers:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '...'
```

En OpenAI Platform, esto debería configurarse automáticamente.

### ChatGPT no encuentra mis herramientas

**Síntomas**: ChatGPT dice "I don't have access to that tool".

**Diagnóstico**:

1. ✅ Verifica que el endpoint MCP está configurado correctamente en OpenAI Platform

2. ✅ Verifica que ngrok está corriendo:

```bash
ngrok http 8000
```

3. ✅ Prueba el endpoint de herramientas:

```bash
curl -X POST https://tu-ngrok-url/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

4. ✅ Inicia una nueva conversación en ChatGPT (las herramientas se cargan al inicio)

### Error de validación de Pydantic

**Síntomas**: Errores como "validation error" o "field required".

**Solución**:

1. Verifica que el `inputSchema` coincide con tu modelo Pydantic:

```python
# Si tu modelo tiene:
class MyInput(BaseModel):
    my_field: str = Field(..., alias="myField")

# Tu inputSchema debe usar el alias:
inputSchema={
    "type": "object",
    "properties": {
        "myField": {"type": "string"},  # Usa el alias
    },
    "required": ["myField"],
}
```

2. Usa `populate_by_name=True` para aceptar ambos nombres:

```python
class MyInput(BaseModel):
    my_field: str = Field(..., alias="myField")
    model_config = ConfigDict(populate_by_name=True)
```

---

## Recursos Adicionales

### Documentación Python Específica
- [Pydantic v2 Documentation](https://docs.pydantic.dev/) - Validación de datos en Python
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Framework web ASGI
- [uvicorn Documentation](https://www.uvicorn.org/) - Servidor ASGI
- [uv Documentation](https://docs.astral.sh/uv/) - Gestor de paquetes Python
- [pytest Documentation](https://docs.pytest.org/) - Framework de testing

### MCP y OpenAI Apps SDK
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - SDK oficial de MCP para Python
- [MCP Specification](https://modelcontextprotocol.io/specification) - Especificación del protocolo
- [OpenAI Apps SDK Examples](https://github.com/openai/openai-apps-sdk-examples) - Ejemplos oficiales
- [OpenAI Apps SDK Docs](https://developers.openai.com/apps-sdk/) - Documentación oficial

### Herramientas Python
- [typing Documentation](https://docs.python.org/3/library/typing.html) - Type hints en Python
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html) - Programación asíncrona
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para Python
- [Alembic](https://alembic.sqlalchemy.org/) - Migraciones de base de datos

---

**¿No encuentras lo que buscas?**

- Consulta [EXPLANATION.md](./EXPLANATION.md) para entender conceptos profundos sobre la arquitectura Python
- Ve los tutoriales en [tutorials/](./tutorials/) para recorridos paso a paso
- Revisa el código fuente en `../src/todo_app/` para ejemplos reales de implementación Python
