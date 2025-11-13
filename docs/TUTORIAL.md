# Tutorial: Construye tu Primera App con OpenAI Apps SDK

> **Tipo de documento**: Tutorial (Learning-oriented)
> **Objetivo**: Aprender a crear una aplicación funcional con OpenAI Apps SDK desde cero
> **Tiempo estimado**: 60-90 minutos
> **Nivel**: Principiante

## Introducción

En este tutorial, aprenderás a construir una aplicación de notas (notes app) completamente funcional que se integra con ChatGPT usando el OpenAI Apps SDK. Al finalizar, tendrás:

- Una aplicación funcional con servidor MCP
- Herramientas que ChatGPT puede usar
- Un widget interactivo visible en ChatGPT
- Comprensión práctica del flujo completo

**Lo que construirás**: Una aplicación simple de notas donde podrás crear, listar y eliminar notas a través de ChatGPT.

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.11 o superior
- Un editor de código (VS Code, PyCharm, etc.)
- Una terminal
- Cuenta en ngrok (gratuita)

## Paso 1: Configurar el Entorno

Primero, vamos a crear un nuevo proyecto y configurar el entorno Python.

### 1.1 Crear el directorio del proyecto

```bash
mkdir my-notes-app
cd my-notes-app
```

### 1.2 Instalar uv (gestor de paquetes Python)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 1.3 Crear el entorno virtual

```bash
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 1.4 Crear pyproject.toml

Crea un archivo `pyproject.toml` con este contenido:

```toml
[project]
name = "my-notes-app"
version = "0.1.0"
description = "A simple notes app using OpenAI Apps SDK"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.31.0",
    "mcp[fastapi]>=0.1.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 1.5 Instalar dependencias

```bash
uv sync
```

**✅ Checkpoint**: Deberías ver que las dependencias se instalaron correctamente sin errores.

## Paso 2: Crear el Modelo de Datos

Ahora vamos a definir cómo se verá una nota en nuestra aplicación.

### 2.1 Crear la estructura de directorios

```bash
mkdir -p src/notes_app
touch src/notes_app/__init__.py
```

### 2.2 Crear models.py

Crea el archivo `src/notes_app/models.py`:

```python
"""Data models for the Notes application"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Note(BaseModel):
    """A single note"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "1",
                "title": "My First Note",
                "content": "This is the content of my note"
            }
        }
    )

    id: str = Field(..., description="Unique identifier for the note")
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )


class NoteCreate(BaseModel):
    """Model for creating a new note"""
    title: str = Field(..., min_length=1, description="Title of the note")
    content: str = Field(..., description="Content of the note")
```

**🎓 Aprendiste**: Cómo usar Pydantic para definir modelos de datos con validación automática.

## Paso 3: Crear el Sistema de Almacenamiento

Vamos a crear un sistema simple para almacenar notas en memoria.

### 3.1 Crear storage.py

Crea el archivo `src/notes_app/storage.py`:

```python
"""In-memory storage for notes"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from .models import Note, NoteCreate


class NotesStorage:
    """Simple in-memory storage for notes"""

    def __init__(self):
        self._notes: Dict[str, Note] = {}

    def create(self, note_create: NoteCreate) -> Note:
        """Create a new note"""
        note = Note(
            id=str(uuid4()),
            title=note_create.title,
            content=note_create.content,
            created_at=datetime.utcnow()
        )
        self._notes[note.id] = note
        return note

    def list(self) -> List[Note]:
        """List all notes"""
        return list(self._notes.values())

    def get(self, note_id: str) -> Optional[Note]:
        """Get a specific note by ID"""
        return self._notes.get(note_id)

    def delete(self, note_id: str) -> bool:
        """Delete a note by ID"""
        if note_id in self._notes:
            del self._notes[note_id]
            return True
        return False

    def count(self) -> int:
        """Count total notes"""
        return len(self._notes)


# Global storage instance
storage = NotesStorage()
```

**🎓 Aprendiste**: Cómo crear un sistema de almacenamiento simple usando diccionarios de Python.

## Paso 4: Crear el Servidor MCP

Aquí es donde la magia sucede. Vamos a crear el servidor MCP que ChatGPT usará.

### 4.1 Crear mcp_server.py

Crea el archivo `src/notes_app/mcp_server.py`:

```python
"""MCP Server for Notes App"""

import os
from typing import Any, Dict, List

import mcp.types as types
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from .models import NoteCreate
from .storage import storage

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP(
    name="notes-app",
    stateless_http=True,
)


# Input schema for creating notes
class CreateNoteInput(BaseModel):
    """Schema for creating a note"""
    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The content of the note")


# Input schema for deleting notes
class DeleteNoteInput(BaseModel):
    """Schema for deleting a note"""
    note_id: str = Field(..., alias="noteId", description="The ID of the note to delete")


@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List all available tools"""
    return [
        types.Tool(
            name="create_note",
            title="Create Note",
            description="Create a new note with title and content",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the note"},
                    "content": {"type": "string", "description": "The content of the note"},
                },
                "required": ["title", "content"],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="list_notes",
            title="List Notes",
            description="List all notes",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="delete_note",
            title="Delete Note",
            description="Delete a note by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "noteId": {"type": "string", "description": "The ID of the note to delete"},
                },
                "required": ["noteId"],
                "additionalProperties": False,
            },
        ),
    ]


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool call requests"""
    tool_name = req.params.name
    arguments = req.params.arguments or {}

    if tool_name == "create_note":
        payload = CreateNoteInput.model_validate(arguments)
        note_create = NoteCreate(title=payload.title, content=payload.content)
        note = storage.create(note_create)

        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"✅ Created note: {note.title}",
                    )
                ],
                structuredContent={"note": note.model_dump(mode='json')},
            )
        )

    elif tool_name == "list_notes":
        notes = storage.list()
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Found {len(notes)} notes",
                    )
                ],
                structuredContent={
                    "notes": [note.model_dump(mode='json') for note in notes],
                    "count": len(notes),
                },
            )
        )

    elif tool_name == "delete_note":
        payload = DeleteNoteInput.model_validate(arguments)
        if storage.delete(payload.note_id):
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text="✅ Note deleted successfully",
                        )
                    ],
                )
            )
        else:
            return types.ServerResult(
                types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text="❌ Note not found",
                        )
                    ],
                    isError=True,
                )
            )

    else:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool: {tool_name}",
                    )
                ],
                isError=True,
            )
        )


# Register the tool handler
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
```

**🎓 Aprendiste**: Cómo definir herramientas MCP que ChatGPT puede descubrir y usar.

## Paso 5: Crear el Servidor Principal

Ahora vamos a crear la aplicación principal que expondrá el servidor MCP.

### 5.1 Crear main.py

Crea el archivo `src/notes_app/main.py`:

```python
"""Main application entry point"""

from starlette.middleware.cors import CORSMiddleware
from .mcp_server import mcp

# Get MCP app
app = mcp.streamable_http_app()

# Add CORS middleware for OpenAI Apps SDK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.notes_app.main:app", host="0.0.0.0", port=8000, reload=True)
```

**🎓 Aprendiste**: Cómo configurar una aplicación Starlette con CORS para que funcione con OpenAI.

## Paso 6: Probar Localmente

Vamos a ejecutar el servidor y probarlo.

### 6.1 Iniciar el servidor

```bash
uv run uvicorn src.notes_app.main:app --reload --port 8000
```

Deberías ver:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 6.2 Probar el endpoint MCP

En otra terminal, prueba listar las herramientas:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

Deberías ver una respuesta JSON con las tres herramientas: `create_note`, `list_notes`, y `delete_note`.

**✅ Checkpoint**: Si ves las herramientas en la respuesta, ¡tu servidor MCP está funcionando!

## Paso 7: Exponer el Servidor con ngrok

Para que ChatGPT pueda comunicarse con tu aplicación local, necesitas exponerla a internet.

### 7.1 Instalar ngrok

Ve a [ngrok.com](https://ngrok.com), crea una cuenta gratuita y descarga ngrok.

### 7.2 Autenticar ngrok

```bash
ngrok authtoken TU_AUTH_TOKEN
```

### 7.3 Iniciar el túnel

En una nueva terminal:

```bash
ngrok http 8000
```

Copia la URL HTTPS que ngrok te proporciona (ejemplo: `https://abc123.ngrok-free.dev`).

**🎓 Aprendiste**: Cómo usar ngrok para exponer servicios locales a internet de forma segura.

## Paso 8: Conectar con OpenAI Apps SDK

Ahora viene la parte emocionante: conectar tu aplicación con ChatGPT.

### 8.1 Ir a OpenAI Platform

1. Ve a [platform.openai.com/apps](https://platform.openai.com/apps)
2. Haz clic en "Create new app"
3. Nombra tu aplicación "My Notes App"

### 8.2 Configurar el endpoint MCP

1. En la sección de configuración, busca "MCP Server Endpoint"
2. Ingresa: `https://TU-URL-DE-NGROK/mcp`
3. Asegúrate de incluir `/mcp` al final
4. Guarda la configuración

### 8.3 Activar la aplicación en ChatGPT

1. Ve a [chat.openai.com](https://chat.openai.com)
2. Haz clic en tu perfil
3. Ve a "Settings" → "Beta features"
4. Activa "Apps" si no lo está
5. En el chat, busca tu aplicación en el selector de apps

**✅ Checkpoint**: Deberías poder ver tu aplicación en la lista de apps disponibles en ChatGPT.

## Paso 9: ¡Prueba tu Aplicación!

Ahora es momento de probar todo junto.

### 9.1 Crear una nota

En ChatGPT, escribe:

```
Create a note with title "Shopping List" and content "Milk, Eggs, Bread"
```

Deberías ver que ChatGPT usa tu herramienta y confirma que la nota fue creada.

### 9.2 Listar notas

Escribe:

```
Show me all my notes
```

ChatGPT debería mostrar la nota que acabas de crear.

### 9.3 Eliminar una nota

Primero obtén el ID de la nota de la lista, luego:

```
Delete the note with ID [el-id-que-copiaste]
```

**🎉 ¡Felicidades!** Has creado tu primera aplicación completa con OpenAI Apps SDK.

## Paso 10: Agregar un Widget (Extra)

Vamos a añadir una interfaz visual que se muestra en ChatGPT.

### 10.1 Actualizar mcp_server.py

Agrega este código al inicio del archivo, después de los imports:

```python
# Widget configuration
WIDGETS_URI = "ui://widget/notes-list.html"
MIME_TYPE = "text/html+skybridge"

def _get_notes_html() -> str:
    """Generate HTML for notes widget"""
    notes = storage.list()

    notes_html = ""
    for note in notes:
        notes_html += f"""
        <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin: 8px 0;">
            <h3 style="margin: 0 0 8px 0; color: #111827;">{note.title}</h3>
            <p style="margin: 0; color: #6b7280;">{note.content}</p>
            <small style="color: #9ca3af;">Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}</small>
        </div>
        """

    if not notes_html:
        notes_html = "<p style='text-align: center; color: #9ca3af;'>No notes yet. Create one!</p>"

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Notes</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 16px; background: white;">
    <h2 style="color: #111827; margin-top: 0;">📝 My Notes</h2>
    {notes_html}
</body>
</html>"""
```

### 10.2 Actualizar list_tools

Modifica la herramienta `list_notes` para incluir metadata del widget:

```python
types.Tool(
    name="list_notes",
    title="List Notes",
    description="List all notes with visual interface",
    inputSchema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    _meta={
        "openai/outputTemplate": WIDGETS_URI,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    },
),
```

### 10.3 Agregar handlers de recursos

Agrega estas funciones antes de registrar el handler de tools:

```python
@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    """List all widget resources"""
    return [
        types.Resource(
            name="Notes List Widget",
            title="Notes List",
            uri=WIDGETS_URI,
            description="Visual display of all notes",
            mimeType=MIME_TYPE,
        )
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    """Handle resource read requests for widget HTML"""
    if str(req.params.uri) == WIDGETS_URI:
        html = _get_notes_html()
        contents = [
            types.TextResourceContents(
                uri=WIDGETS_URI,
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


# Register resource handler
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource
```

### 10.4 Probar el widget

1. Reinicia tu servidor
2. En ChatGPT, escribe: "Show me my notes"
3. Deberías ver un widget visual con tus notas

**🎓 Aprendiste**: Cómo crear widgets HTML que se renderizan en ChatGPT.

## Resumen

¡Felicidades por completar el tutorial! Has aprendido a:

- ✅ Configurar un proyecto Python con OpenAI Apps SDK
- ✅ Crear modelos de datos con Pydantic
- ✅ Implementar un sistema de almacenamiento
- ✅ Construir un servidor MCP funcional
- ✅ Definir herramientas que ChatGPT puede usar
- ✅ Exponer tu aplicación con ngrok
- ✅ Conectar tu app con la plataforma OpenAI
- ✅ Crear widgets visuales interactivos

## Próximos Pasos

Ahora que tienes una base sólida, puedes:

1. **Leer la guía de How-to** (`GUIDE.md`) para aprender tareas específicas
2. **Explorar el documento de Explanation** (`EXPLANATION.md`) para entender conceptos profundos
3. **Agregar más funcionalidades**: editar notas, agregar tags, búsqueda
4. **Implementar persistencia**: usar SQLite o PostgreSQL en lugar de almacenamiento en memoria
5. **Crear widgets más complejos**: con formularios, estilos avanzados, interactividad

## Recursos Adicionales

- [Documentación oficial de MCP](https://modelcontextprotocol.io/)
- [OpenAI Apps SDK Documentation](https://developers.openai.com/apps-sdk/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Ayuda y Soporte

Si encontraste algún problema durante el tutorial:

1. Verifica que todas las dependencias estén instaladas correctamente
2. Asegúrate de que ngrok esté corriendo y la URL sea correcta
3. Revisa los logs del servidor para ver errores específicos
4. Consulta la sección de troubleshooting en `GUIDE.md`

---

**¡Feliz construcción!** 🚀
