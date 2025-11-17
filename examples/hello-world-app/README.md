# Hola Mundo App - Ejemplo de OpenAI Apps SDK

Este es el código de ejemplo completo para el [Tutorial Hola Mundo](../../docs/tutorials/hello-world-tutorial.md).

## 🚀 Inicio Rápido

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Instalar dependencias
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
uv sync

# 3. Ejecutar el servidor
just dev
# O sin just:
uv run uvicorn src.hello_app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: http://localhost:8000

## 📁 Estructura

```
hello-world-app/
├── src/
│   └── hello_app/
│       ├── __init__.py      # Módulo Python
│       ├── main.py          # FastAPI + integración MCP
│       └── mcp_server.py    # Servidor MCP con herramientas y widgets
├── pyproject.toml           # Dependencias del proyecto
├── justfile                 # Comandos útiles
├── .env.example             # Template de variables de entorno
└── README.md                # Este archivo
```

## 🧪 Probar

### Verificar que el servidor está corriendo

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

### Listar herramientas MCP disponibles

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

### Llamar la herramienta say_hello

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

## 🌍 Conectar con ChatGPT

1. **Instalar y ejecutar ngrok:**
   ```bash
   ngrok http 8000
   ```

2. **Copiar la URL de ngrok** (ej: `https://abc123.ngrok.app`)

3. **Actualizar .env:**
   ```bash
   PUBLIC_URL=https://abc123.ngrok.app
   ```

4. **Reiniciar el servidor**

5. **Ir a OpenAI Platform:**
   - Visita: https://platform.openai.com/playground/apps
   - Crea una nueva app
   - MCP Server URL: `https://abc123.ngrok.app/mcp`

6. **Probar en ChatGPT:**
   ```
   "Usa la app Hola Mundo para saludar a María"
   ```

   O para ver el widget:
   ```
   "Muéstrame el widget de Hola Mundo"
   ```

## 📚 Documentación

Para el tutorial completo paso a paso, visita:
- [Tutorial Hola Mundo](../../docs/tutorials/hello-world-tutorial.md)

## 🎓 ¿Qué aprendiste?

- ✅ Crear un servidor MCP con FastMCP
- ✅ Definir herramientas MCP con `@mcp.tool()`
- ✅ Crear widgets interactivos con `@mcp.resource()`
- ✅ Usar `window.openai.callTool()` en JavaScript
- ✅ Integrar MCP con FastAPI
- ✅ Exponer tu servidor con ngrok
- ✅ Conectar con ChatGPT

## 🚀 Siguientes Pasos

Ahora que dominas lo básico, continúa con:
- [Tutorial de ToDo App](../../docs/tutorials/todo-app-tutorial.md) - App completa con CRUD
- [Tutorial de Notes App](../../docs/tutorials/notes-app-tutorial.md) - Construcción desde cero

---

**¡Feliz desarrollo!** 🎉
