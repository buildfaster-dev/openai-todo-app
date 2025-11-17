# Tutorial: Hola Mundo con OpenAI Apps SDK

**Nivel**: Principiante absoluto
**Tiempo**: 30-45 minutos
**Objetivo**: Entender el flujo básico de MCP, UI y ChatGPT

## 🎯 ¿Qué vamos a construir?

Una aplicación super simple que:
1. Tiene una herramienta MCP que dice "Hola" a quien tú quieras
2. Muestra un widget visual en ChatGPT
3. Te permite entender cómo fluye la información

**No vamos a usar bases de datos, ni CRUD complejo** - solo lo mínimo para entender.

## 📚 Conceptos Básicos (2 minutos de lectura)

### ¿Qué es MCP?

**MCP (Model Context Protocol)** es como un "idioma" que permite a ChatGPT comunicarse con tu aplicación.

```
ChatGPT: "Oye app, ¿qué puedes hacer?"
Tu App MCP: "Puedo decir hola a las personas"
ChatGPT: "Ok, dile hola a María"
Tu App MCP: "¡Hola María! 👋"
```

### Los 3 Componentes

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   ChatGPT   │ ◄─────► │  MCP Server  │ ◄─────► │  UI Widget  │
│             │  JSON   │  (Python)    │  HTTP   │   (HTML)    │
└─────────────┘         └──────────────┘         └─────────────┘
```

1. **ChatGPT**: Interpreta lo que el usuario quiere
2. **MCP Server**: Tu código Python que hace el trabajo
3. **UI Widget**: Interfaz visual bonita (HTML + JavaScript)

## 🚀 Paso 1: Estructura del Proyecto

Vamos a crear un proyecto mínimo llamado `hello-world-app`:

```bash
mkdir hello-world-app
cd hello-world-app

# Crear estructura de carpetas
mkdir -p src/hello_app
touch src/hello_app/__init__.py
touch src/hello_app/main.py
touch src/hello_app/mcp_server.py
```

Tu estructura quedará así:

```
hello-world-app/
├── src/
│   └── hello_app/
│       ├── __init__.py      # Vacío (marca el paquete Python)
│       ├── main.py          # FastAPI + MCP integration
│       └── mcp_server.py    # La lógica MCP
├── pyproject.toml           # Dependencias
├── justfile                 # Comandos útiles
└── .env                     # Configuración
```

## 📦 Paso 2: Configurar Dependencias

Crea `pyproject.toml`:

```toml
[project]
name = "hello-world-app"
version = "0.1.0"
description = "Tutorial Hola Mundo con OpenAI Apps SDK"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "mcp[fastapi]>=0.1.0",
    "python-dotenv>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**¿Qué hace cada dependencia?**
- `fastapi`: Servidor web moderno y rápido
- `uvicorn`: Ejecuta el servidor
- `pydantic`: Validación de datos
- `mcp[fastapi]`: El SDK de OpenAI Apps
- `python-dotenv`: Lee variables de entorno

Instalar:

```bash
# Opción 1: Con uv (recomendado)
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
uv sync

# Opción 2: Con pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 🔧 Paso 3: Crear el Servidor MCP

Ahora viene la magia. Crea `src/hello_app/mcp_server.py`:

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

### 🔍 Análisis del Código

**¿Qué acabamos de hacer?**

1. **`FastMCP("Hola Mundo App")`**: Crea el servidor MCP
2. **`@mcp.tool()`**: Registra una función como herramienta que ChatGPT puede usar
3. **`SayHelloInput`**: Define qué parámetros acepta la herramienta
4. **`@mcp.resource()`**: Crea un widget HTML que se muestra en ChatGPT
5. **`window.openai.callTool()`**: API de JavaScript para llamar herramientas MCP desde el UI

## 🌐 Paso 4: Integrar con FastAPI

Ahora crea `src/hello_app/main.py`:

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

# Crear la aplicación FastAPI desde el servidor MCP
# Esto convierte tu servidor MCP en una aplicación web
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

### 🔍 Conceptos Clave

- **`app.mount("/mcp", ...)`**: Expone tu servidor MCP en `http://localhost:8000/mcp`
- **CORS**: Sin esto, el navegador bloquearía las llamadas desde ChatGPT
- **`/` endpoint**: Para verificar que el servidor está corriendo

## ⚙️ Paso 5: Configuración

Crea un archivo `.env`:

```bash
# URL pública de tu aplicación
# Durante desarrollo local:
PUBLIC_URL=http://localhost:8000

# Cuando uses ngrok, cambiarás esto a:
# PUBLIC_URL=https://tu-url-ngrok.app
```

Crea un `justfile` para comandos fáciles:

```makefile
# Comandos útiles para el proyecto

# Instalar dependencias
install:
    uv sync

# Ejecutar servidor de desarrollo
dev:
    uv run uvicorn src.hello_app.main:app --reload --host 0.0.0.0 --port 8000

# Ver info
info:
    @echo "Hola Mundo App"
    @echo "=============="
    @echo "Server: http://localhost:8000"
    @echo "MCP Endpoint: http://localhost:8000/mcp"
```

## 🎬 Paso 6: ¡Ejecutar!

```bash
# Asegúrate de estar en el directorio del proyecto
cd hello-world-app

# Ejecutar el servidor
just dev

# O sin just:
uv run uvicorn src.hello_app.main:app --reload --host 0.0.0.0 --port 8000
```

Deberías ver:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**¡Felicidades! Tu servidor MCP está corriendo.** 🎉

## 🧪 Paso 7: Probar Localmente

Antes de conectar con ChatGPT, probemos que funciona:

### Verificar que el servidor está vivo

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

### Listar herramientas disponibles

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

Deberías ver la herramienta `say_hello` listada.

### Llamar la herramienta directamente

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

Deberías ver: `¡Hola Claude! 👋`

## 🌍 Paso 8: Exponer con ngrok

Para que ChatGPT pueda acceder a tu servidor local, necesitas exponerlo a Internet:

```bash
# Instalar ngrok (si no lo tienes)
# Visita https://ngrok.com y crea una cuenta gratuita

# Exponer el puerto 8000
ngrok http 8000
```

Verás algo como:

```
Forwarding   https://abc123.ngrok.app -> http://localhost:8000
```

**Copia esa URL de ngrok** (ej: `https://abc123.ngrok.app`)

Actualiza tu `.env`:

```bash
PUBLIC_URL=https://abc123.ngrok.app
```

**Reinicia el servidor** para que tome la nueva URL.

## 🤖 Paso 9: Conectar con ChatGPT

### 1. Ir a OpenAI Platform

Visita: https://platform.openai.com/playground/apps

### 2. Crear una nueva app

- Click en "Create App"
- Nombre: "Hola Mundo App"
- MCP Server URL: `https://tu-url-ngrok.ngrok.app/mcp`

### 3. Probar en ChatGPT

Ahora en ChatGPT, puedes decir:

```
"Usa la app Hola Mundo para saludar a María"
```

ChatGPT debería:
1. Llamar a tu herramienta `say_hello`
2. Recibir `¡Hola María! 👋`
3. Mostrarte el resultado

### 4. Ver el Widget

También puedes decir:

```
"Muéstrame el widget de Hola Mundo"
```

ChatGPT mostrará tu interfaz HTML interactiva donde puedes:
- Escribir un nombre
- Elegir si quieres emoji
- Hacer clic en "¡Saludar!"
- Ver el resultado

## 🔄 Entendiendo el Flujo Completo

Aquí está lo que sucede cuando haces clic en "¡Saludar!" en el widget:

```
┌──────────────────────────────────────────────────────────────┐
│  1. Usuario escribe "María" y hace clic en "¡Saludar!"      │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  2. JavaScript ejecuta: window.openai.callTool({             │
│       name: 'say_hello',                                     │
│       parameters: { name: 'María', emoji: true }             │
│     })                                                       │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  3. OpenAI Platform recibe la solicitud y la envía al MCP   │
│     POST https://tu-app.ngrok.app/mcp                        │
│     {                                                        │
│       "method": "tools/call",                                │
│       "params": {                                            │
│         "name": "say_hello",                                 │
│         "arguments": { "name": "María", "emoji": true }      │
│       }                                                      │
│     }                                                        │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Tu servidor MCP (mcp_server.py) recibe la llamada       │
│     - Valida los parámetros con Pydantic                     │
│     - Ejecuta la función say_hello()                         │
│     - Genera: "¡Hola María! 👋"                              │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Respuesta regresa a través de MCP → OpenAI → Widget     │
│     El JavaScript muestra: "¡Hola María! 👋"                 │
└──────────────────────────────────────────────────────────────┘
```

### Flujo desde ChatGPT (conversación natural)

```
┌──────────────────────────────────────────────────────────────┐
│  1. Usuario: "Saluda a Pedro usando la app Hola Mundo"      │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  2. ChatGPT analiza el mensaje y decide:                    │
│     "Necesito usar la herramienta say_hello"                 │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  3. ChatGPT llama al MCP de tu app:                          │
│     tools/call -> say_hello(name="Pedro", emoji=true)        │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Tu app procesa y responde: "¡Hola Pedro! 👋"             │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  5. ChatGPT muestra al usuario:                              │
│     "He saludado a Pedro: ¡Hola Pedro! 👋"                   │
└──────────────────────────────────────────────────────────────┘
```

## 🎓 Conceptos Que Aprendiste

### 1. MCP Tools
- Son funciones Python decoradas con `@mcp.tool()`
- ChatGPT puede llamarlas cuando las necesita
- Usan Pydantic para validar inputs

### 2. MCP Resources
- Son contenido que se puede mostrar (HTML, datos, etc.)
- Se identifican con URIs como `ui://widget/hello.html`
- Pueden ser widgets interactivos

### 3. window.openai API
- **`window.openai.callTool()`**: Llama herramientas MCP desde JavaScript
- Solo funciona dentro de widgets de OpenAI Apps SDK
- Permite crear UIs interactivas

### 4. Transporte HTTP
- MCP puede funcionar sobre HTTP (como este tutorial)
- También soporta stdio y SSE
- HTTP es mejor para apps web

### 5. JSON-RPC 2.0
- Protocolo que usa MCP para comunicación
- Métodos importantes:
  - `tools/list`: Listar herramientas disponibles
  - `tools/call`: Ejecutar una herramienta
  - `resources/list`: Listar recursos disponibles
  - `resources/read`: Leer un recurso (ej: widget HTML)

## 🚀 Siguientes Pasos

Ahora que entiendes lo básico, puedes:

### Nivel 1: Modificaciones Simples
- Cambia el emoji por otros: 🎉, 🌟, 💫
- Añade más parámetros: idioma, hora del día (buenos días/tardes)
- Cambia los colores del widget

### Nivel 2: Nueva Herramienta
- Añade una herramienta `farewell` que se despida
- Crea un widget para despedidas
- Prueba con ChatGPT

### Nivel 3: Con Datos
- Lee el tutorial de ToDo App o Notes App
- Aprende a guardar datos
- Crea APIs REST

## 🐛 Troubleshooting

### Error: "Module not found"

```bash
# Asegúrate de instalar las dependencias
uv sync

# Verifica que estás en el directorio correcto
pwd  # Debería mostrar .../hello-world-app
```

### Error: "Address already in use"

```bash
# El puerto 8000 ya está en uso
# Mata el proceso anterior:
lsof -ti:8000 | xargs kill -9

# O usa otro puerto:
uvicorn src.hello_app.main:app --reload --port 8001
```

### Widget no se conecta con MCP

1. Verifica que `PUBLIC_URL` en `.env` es tu URL de ngrok
2. Reinicia el servidor después de cambiar `.env`
3. Verifica que ngrok está corriendo

### ChatGPT no ve mi app

1. Verifica que la URL de ngrok es correcta
2. Asegúrate de agregar `/mcp` al final: `https://tu-url.ngrok.app/mcp`
3. Verifica que CORS está habilitado

## 📚 Recursos Adicionales

- [Tutorial de ToDo App](./todo-app-tutorial.md) - App completa con CRUD
- [Tutorial de Notes App](./notes-app-tutorial.md) - Construcción desde cero
- [MCP Specification](https://modelcontextprotocol.io/) - Documentación oficial
- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk/) - Guía de OpenAI

## ✅ Checklist de Completitud

- [ ] Entiendo qué es MCP
- [ ] Sé cómo crear una herramienta con `@mcp.tool()`
- [ ] Sé cómo crear un widget con `@mcp.resource()`
- [ ] Entiendo el flujo: ChatGPT → MCP → Python → Respuesta
- [ ] Sé usar `window.openai.callTool()` en JavaScript
- [ ] He conectado mi app con ChatGPT
- [ ] He visto el widget funcionando
- [ ] Entiendo cómo usar ngrok para exponer mi servidor

## 🎉 ¡Felicidades!

Has completado tu primera app con OpenAI Apps SDK. Ahora entiendes:
- Cómo MCP conecta ChatGPT con tu código
- Cómo crear herramientas que ChatGPT puede usar
- Cómo crear UIs interactivas con widgets
- El flujo completo de datos

**Estás listo para construir apps más complejas.** 🚀

---

**¿Preguntas?** Revisa la documentación o prueba los otros tutoriales.

**Siguiente**: [Tutorial de ToDo App](./todo-app-tutorial.md) para ver una app completa con base de datos.
