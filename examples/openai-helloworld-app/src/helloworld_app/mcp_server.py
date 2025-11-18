"""Servidor MCP simple - Solo dice Hola."""

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import os

# 1. Crear el servidor MCP
mcp = FastMCP("Hola Mundo App")

# 2. Definir el modelo de entrada para la herramienta
class SayHelloInput(BaseModel):
    """Entrada para decir hola."""
    name: str = Field(description="Nombre de la persona a saludar")
    emoji: bool = Field(default=True, description="¿Incluir emoji?")

# 3. Crear una herramienta MCP simple
@mcp.tool()
def say_hello(input: SayHelloInput) -> str:
    """Dice hola a alguien de manera amigable.

    Esta es la función que ChatGPT puede llamar.
    """
    greeting = f"¡Hola {input.name}!"
    if input.emoji:
        greeting += " 👋"

    return greeting

# 3b. Definir handlers de MCP de bajo nivel para la herramienta de widget
# Esto nos permite usar metadatos de OpenAI que FastMCP no soporta directamente

@mcp._mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Lista todas las herramientas disponibles"""
    return [
        # Herramienta say_hello
        types.Tool(
            name="say_hello",
            description="Dice hola a alguien de manera amigable",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nombre de la persona a saludar"
                    },
                    "emoji": {
                        "type": "boolean",
                        "description": "¿Incluir emoji?",
                        "default": True
                    }
                },
                "required": ["name"],
                "additionalProperties": False
            }
        ),
        # Herramienta show_hello_widget con metadatos de OpenAI
        types.Tool(
            name="show_hello_widget",
            description="Muestra el widget interactivo de saludos donde puedes escribir nombres y generar saludos personalizados",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
            _meta={
                "openai/outputTemplate": "ui://widget/hello.html",
                "openai/widgetAccessible": True,
            }
        )
    ]

@mcp._mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> types.CallToolResult:
    """Maneja llamadas a herramientas"""

    if name == "say_hello":
        # Validar entrada
        input_data = SayHelloInput(**arguments)
        # Generar saludo
        greeting = f"¡Hola {input_data.name}!"
        if input_data.emoji:
            greeting += " 👋"

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=greeting
                )
            ]
        )

    elif name == "show_hello_widget":
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text="Widget de saludos cargado. Usa la interfaz para crear saludos personalizados."
                )
            ],
            _meta={
                "openai/toolInvocation/invoking": "Abriendo el widget de saludos...",
                "openai/toolInvocation/invoked": "Widget de saludos abierto",
            }
        )

    raise ValueError(f"Herramienta desconocida: {name}")

# 4. Definir el HTML del widget como recurso
@mcp.resource("ui://widget/hello.html")
def get_hello_widget_html() -> str:
    """HTML del widget visual que muestra la aplicación de saludos."""

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
