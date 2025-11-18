# Tutorial: Agregando Widgets Interactivos a tu App MCP

> **Tipo de Documento**: Tutorial (Orientado al aprendizaje)
> **Objetivo**: Crear widgets HTML interactivos para ChatGPT
> **Tiempo Estimado**: 30-45 minutos
> **Nivel**: Intermedio
> **Prerequisito**: [Tutorial Hola Mundo](./hello-world-tutorial.md) completado

## Objetivos de Aprendizaje

Al final de este tutorial, entenderás:

1. **Qué son los recursos MCP** - Cómo exponer contenido HTML a ChatGPT
2. **Cómo crear widgets con `@mcp.resource()`** - Registrar interfaces visuales
3. **El formato `text/html+skybridge`** - MIME type para widgets HTML
4. **Cómo usar `window.openai.callTool()`** - API JavaScript para llamar herramientas MCP
5. **El flujo Widget ↔ MCP** - Comunicación bidireccional entre UI y servidor
6. **Evolución de widgets** - De estático a interactivo paso a paso

## Introducción

En el tutorial de Hola Mundo, creaste una herramienta MCP simple que ChatGPT puede llamar. Ahora vas a **agregar una interfaz visual interactiva** (widget) que se mostrará directamente en ChatGPT.

**Lo que construirás**: Un widget HTML que permite al usuario ingresar un nombre y emoji, llamar a tu herramienta `say_hello` con un botón, y ver el resultado en tiempo real.

**Progresión del tutorial**:
```
Versión 1: Widget estático básico (solo HTML)
    ↓
Versión 2: Agregar estilos CSS
    ↓
Versión 3: Mostrar datos dinámicos
    ↓
Versión 4: Interactividad con window.openai
    ↓
Versión 5: Widget final pulido con UX completa
```

---

## Tabla de Contenidos

- [Prerequisitos](#prerequisitos)
- [Parte 1: Widget Estático Básico](#parte-1-widget-estático-básico)
- [Parte 2: Agregando Estilos CSS](#parte-2-agregando-estilos-css)
- [Parte 3: Datos Dinámicos](#parte-3-datos-dinámicos)
- [Parte 4: Interactividad con window.openai](#parte-4-interactividad-con-windowopenai)
- [Parte 5: Widget Final Pulido](#parte-5-widget-final-pulido)
- [Resumen](#resumen)
- [Siguientes Pasos](#siguientes-pasos)
- [Troubleshooting](#troubleshooting)

---

## Prerequisitos

### ✅ Antes de Empezar

**Debes haber completado**:
- [Tutorial Hola Mundo](./hello-world-tutorial.md) - Tu proyecto `openai-helloworld-app` debe estar funcionando

**Verificar que tienes**:
```bash
# 1. Directorio del proyecto del Hola Mundo
cd openai-helloworld-app

# 2. Entorno Nix activo
nix develop

# 3. Servidor puede iniciar
just dev
# Presiona Ctrl+C para detener

# 4. Archivo .env existe con PUBLIC_URL
cat .env
```

Si todo está bien, continúa. Si no, regresa al [Tutorial Hola Mundo](./hello-world-tutorial.md).

---

## Parte 1: Widget Estático Básico

### 1.1 ¿Qué es un Widget MCP?

Un **widget** es una interfaz HTML que ChatGPT puede mostrar al usuario. Los widgets se exponen como **recursos MCP** usando el decorador `@mcp.resource()`.

**Conceptos clave**:
- **Recurso (Resource)**: Contenido que ChatGPT puede leer (HTML, JSON, texto)
- **URI**: Identificador único del recurso (ej: `ui://widget/hello.html`)
- **MIME type**: `text/html+skybridge` para widgets HTML
- **Template**: HTML que se renderiza en ChatGPT

### 1.2 El Flujo de Widgets

```
Usuario pide en ChatGPT: "Muestra el widget de saludos"
    ↓
ChatGPT llama: resources/list (obtiene lista de widgets disponibles)
    ↓
ChatGPT encuentra: ui://widget/hello.html
    ↓
ChatGPT llama: resources/read con URI ui://widget/hello.html
    ↓
Tu servidor retorna: HTML del widget
    ↓
ChatGPT renderiza el HTML en su interfaz
    ↓
Usuario ve el widget interactivo
```

### 1.3 Agregar el Widget al Servidor MCP

Vamos a modificar `src/helloworld_app/mcp_server.py` para agregar un widget.

**Abrir el archivo**:
```bash
# Desde openai-helloworld-app/
code src/helloworld_app/mcp_server.py
# O usa tu editor preferido
```

**Agregar el widget después de la herramienta `say_hello`**. El archivo completo debe verse así:

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

# 4. NUEVO: Crear el widget (recurso MCP)
@mcp.resource("ui://widget/hello.html")
def hello_widget() -> str:
    """Widget HTML para saludar personas.

    Este recurso retorna HTML que ChatGPT renderiza.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Widget de Saludos</title>
    </head>
    <body>
        <h1>¡Hola Mundo Widget!</h1>
        <p>Este es mi primer widget HTML en ChatGPT.</p>
    </body>
    </html>
    """
    return html
```

**Qué hace esto:**
- `@mcp.resource("ui://widget/hello.html")`: Registra un recurso con URI única
- `def hello_widget() -> str`: Función que retorna HTML
- El HTML es básico por ahora (solo título y párrafo)

### 1.4 Reiniciar el Servidor

```bash
# Si el servidor está corriendo, presiona Ctrl+C para detenerlo
# Luego reinicia:
just dev
```

### 1.5 Verificar que el Widget Existe

En otra terminal, verifica que el recurso está disponible:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "resources/list",
    "id": 1
  }' 2>/dev/null | grep '^data:' | sed 's/^data: //' | jq
```

**✅ Validar:**

Deberías ver un recurso con:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resources": [
      {
        "uri": "ui://widget/hello.html",
        "name": "Widget de Saludos",
        "mimeType": "text/html"
      }
    ]
  }
}
```

Si ves el recurso `ui://widget/hello.html`, ¡tu widget está registrado! ✅

### 1.6 Leer el Contenido del Widget

Ahora solicita el HTML del widget:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "resources/read",
    "params": {
      "uri": "ui://widget/hello.html"
    },
    "id": 2
  }' 2>/dev/null | grep '^data:' | sed 's/^data: //' | jq -r '.result.contents[0].text'
```

**✅ Validar:**

Deberías ver el HTML completo:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Widget de Saludos</title>
</head>
<body>
    <h1>¡Hola Mundo Widget!</h1>
    <p>Este es mi primer widget HTML en ChatGPT.</p>
</body>
</html>
```

Si ves el HTML, ¡tu widget funciona localmente! ✅

🎓 **Aprendiste:**
- Cómo usar `@mcp.resource()` para registrar widgets
- Que los widgets son recursos con URI `ui://widget/*`
- El método `resources/list` para descubrir recursos
- El método `resources/read` para obtener contenido HTML
- FastMCP automáticamente registra recursos y genera el protocolo

---

## Parte 2: Agregando Estilos CSS

### 2.1 Por Qué Agregar Estilos

El widget actual funciona pero se ve básico. Vamos a agregar CSS para hacerlo más atractivo.

**Principios de diseño para widgets**:
- ✅ Estilos **inline** (dentro de `<style>` tags)
- ✅ Sin dependencias externas (no CDNs)
- ✅ Responsive (funciona en diferentes tamaños)
- ✅ Tema claro (ChatGPT usa fondo blanco)

### 2.2 Actualizar el Widget con Estilos

Modifica la función `hello_widget()` en `src/helloworld_app/mcp_server.py`:

```python
@mcp.resource("ui://widget/hello.html")
def hello_widget() -> str:
    """Widget HTML para saludar personas."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Widget de Saludos</title>
        <style>
            /* Reset básico */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 200px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }

            h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            p {
                font-size: 1.2em;
                opacity: 0.9;
            }

            .emoji {
                font-size: 3em;
                margin: 20px 0;
                animation: wave 1s ease-in-out infinite;
            }

            @keyframes wave {
                0%, 100% { transform: rotate(0deg); }
                25% { transform: rotate(20deg); }
                75% { transform: rotate(-20deg); }
            }
        </style>
    </head>
    <body>
        <div class="emoji">👋</div>
        <h1>¡Hola Mundo Widget!</h1>
        <p>Este es mi primer widget HTML en ChatGPT.</p>
    </body>
    </html>
    """
    return html
```

**Qué hace esto:**
- **Reset CSS**: Normaliza márgenes y padding
- **Gradient background**: Gradiente morado/azul atractivo
- **Typography**: Fuente del sistema, tamaños legibles
- **Emoji animado**: Animación de saludo ondulante
- **Flexbox**: Centra el contenido vertical y horizontalmente

### 2.3 Reiniciar y Probar

```bash
# Ctrl+C para detener el servidor
# Luego:
just dev
```

**Verificar el HTML actualizado**:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "resources/read",
    "params": {
      "uri": "ui://widget/hello.html"
    },
    "id": 2
  }' 2>/dev/null | grep '^data:' | sed 's/^data: //' | jq -r '.result.contents[0].text' > /tmp/widget.html
```

**Ver en el navegador**:
```bash
# Abre el HTML en tu navegador para ver cómo se ve
open /tmp/widget.html  # macOS
xdg-open /tmp/widget.html  # Linux
```

**✅ Validar:**

Deberías ver:
- Fondo con gradiente morado/azul
- Emoji 👋 animado (ondeando)
- Título grande "¡Hola Mundo Widget!"
- Texto con sombra y buen contraste

Si el widget se ve bien estilizado, ¡perfecto! ✅

🎓 **Aprendiste:**
- Cómo agregar CSS inline a widgets
- Usar gradientes y animaciones CSS
- Diseño responsive con Flexbox
- Fuentes del sistema para compatibilidad

---

## Parte 3: Datos Dinámicos

### 3.1 Agregar Formulario HTML

Ahora vamos a hacer que el widget sea más útil agregando un formulario donde el usuario pueda ingresar un nombre.

**Actualizar `hello_widget()` en `src/helloworld_app/mcp_server.py`**:

```python
@mcp.resource("ui://widget/hello.html")
def hello_widget() -> str:
    """Widget HTML para saludar personas."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Widget de Saludos</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .container {
                max-width: 400px;
                margin: 0 auto;
            }

            h1 {
                font-size: 2em;
                margin-bottom: 20px;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            .form-group {
                margin-bottom: 15px;
            }

            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
            }

            input[type="text"] {
                width: 100%;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 1em;
            }

            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            button {
                width: 100%;
                padding: 12px;
                background: white;
                color: #667eea;
                border: none;
                border-radius: 5px;
                font-size: 1.1em;
                font-weight: 700;
                cursor: pointer;
                transition: transform 0.2s;
            }

            button:hover {
                transform: scale(1.05);
            }

            .result {
                margin-top: 20px;
                padding: 15px;
                background: rgba(255,255,255,0.2);
                border-radius: 5px;
                text-align: center;
                font-size: 1.5em;
                display: none;
            }

            .result.show {
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👋 Widget de Saludos</h1>

            <div class="form-group">
                <label for="name">Nombre:</label>
                <input type="text" id="name" placeholder="Ingresa tu nombre" value="Mundo">
            </div>

            <div class="form-group">
                <div class="checkbox-group">
                    <input type="checkbox" id="emoji" checked>
                    <label for="emoji">¿Incluir emoji?</label>
                </div>
            </div>

            <button onclick="greet()">Saludar</button>

            <div id="result" class="result"></div>
        </div>

        <script>
            function greet() {
                const name = document.getElementById('name').value;
                const emoji = document.getElementById('emoji').checked;

                // Por ahora, solo mostramos el saludo localmente
                let greeting = `¡Hola ${name}!`;
                if (emoji) {
                    greeting += ' 👋';
                }

                const resultDiv = document.getElementById('result');
                resultDiv.textContent = greeting;
                resultDiv.classList.add('show');
            }
        </script>
    </body>
    </html>
    """
    return html
```

**Qué hace esto:**
- **Formulario**: Input para nombre, checkbox para emoji
- **Botón**: Llama a la función `greet()` cuando se hace clic
- **JavaScript**: Por ahora, solo muestra el saludo localmente (sin llamar al servidor)
- **Div resultado**: Muestra el saludo generado

### 3.2 Probar el Widget

```bash
# Reiniciar servidor
# Ctrl+C y luego:
just dev
```

**Obtener y ver el widget**:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "resources/read",
    "params": {
      "uri": "ui://widget/hello.html"
    },
    "id": 2
  }' 2>/dev/null | grep '^data:' | sed 's/^data: //' | jq -r '.result.contents[0].text' > /tmp/widget.html

# Abrir en navegador
open /tmp/widget.html  # macOS
xdg-open /tmp/widget.html  # Linux
```

**✅ Validar en el navegador:**

1. Deberías ver un formulario con:
   - Input de texto (con "Mundo" por defecto)
   - Checkbox "¿Incluir emoji?" (marcado por defecto)
   - Botón "Saludar"

2. Haz clic en el botón "Saludar"
   - Debería aparecer: "¡Hola Mundo! 👋"

3. Cambia el nombre a "María" y desmarca el emoji
   - Haz clic en "Saludar"
   - Debería aparecer: "¡Hola María!"

Si el formulario funciona y muestra los saludos, ¡perfecto! ✅

🎓 **Aprendiste:**
- Cómo crear formularios HTML en widgets
- Capturar valores de inputs con JavaScript
- Mostrar resultados dinámicamente en el DOM
- Usar eventos `onclick` para interactividad básica

**Nota**: Por ahora el widget genera el saludo localmente con JavaScript. En la siguiente parte, lo conectaremos con la herramienta MCP `say_hello` usando `window.openai.callTool()`.

---

## Parte 4: Interactividad con window.openai

### 4.1 ¿Qué es window.openai?

`window.openai` es una **API JavaScript** que ChatGPT inyecta en los widgets. Permite que tu widget HTML llame a herramientas MCP desde el navegador.

**Métodos disponibles**:
- `window.openai.callTool(name, arguments)`: Llama una herramienta MCP
- Retorna una `Promise` con el resultado de la herramienta

**Flujo**:
```
Usuario hace clic en botón del widget
    ↓
JavaScript llama window.openai.callTool("say_hello", {...})
    ↓
ChatGPT envía solicitud JSON-RPC a tu servidor MCP
    ↓
Tu servidor ejecuta la herramienta say_hello
    ↓
Resultado vuelve a ChatGPT
    ↓
Promise se resuelve con el resultado
    ↓
JavaScript actualiza el DOM con el resultado
```

### 4.2 Actualizar el Widget para Usar window.openai

**Modificar la función `greet()` en `hello_widget()`**:

```python
@mcp.resource("ui://widget/hello.html")
def hello_widget() -> str:
    """Widget HTML para saludar personas."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Widget de Saludos</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .container {
                max-width: 400px;
                margin: 0 auto;
            }

            h1 {
                font-size: 2em;
                margin-bottom: 20px;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            .form-group {
                margin-bottom: 15px;
            }

            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
            }

            input[type="text"] {
                width: 100%;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 1em;
            }

            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            button {
                width: 100%;
                padding: 12px;
                background: white;
                color: #667eea;
                border: none;
                border-radius: 5px;
                font-size: 1.1em;
                font-weight: 700;
                cursor: pointer;
                transition: transform 0.2s;
            }

            button:hover {
                transform: scale(1.05);
            }

            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: scale(1);
            }

            .result {
                margin-top: 20px;
                padding: 15px;
                background: rgba(255,255,255,0.2);
                border-radius: 5px;
                text-align: center;
                font-size: 1.5em;
                display: none;
            }

            .result.show {
                display: block;
            }

            .error {
                background: rgba(255,0,0,0.3);
            }

            .loading {
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👋 Widget de Saludos</h1>

            <div class="form-group">
                <label for="name">Nombre:</label>
                <input type="text" id="name" placeholder="Ingresa tu nombre" value="Mundo">
            </div>

            <div class="form-group">
                <div class="checkbox-group">
                    <input type="checkbox" id="emoji" checked>
                    <label for="emoji">¿Incluir emoji?</label>
                </div>
            </div>

            <button id="greetBtn" onclick="greet()">Saludar</button>

            <div id="result" class="result"></div>
        </div>

        <script>
            async function greet() {
                const name = document.getElementById('name').value;
                const emoji = document.getElementById('emoji').checked;
                const resultDiv = document.getElementById('result');
                const button = document.getElementById('greetBtn');

                // Validación básica
                if (!name.trim()) {
                    resultDiv.textContent = '⚠️ Por favor ingresa un nombre';
                    resultDiv.className = 'result show error';
                    return;
                }

                try {
                    // Deshabilitar botón y mostrar loading
                    button.disabled = true;
                    button.textContent = 'Saludando...';
                    resultDiv.textContent = '⏳ Llamando al servidor MCP...';
                    resultDiv.className = 'result show loading';

                    // Llamar a la herramienta MCP say_hello
                    const result = await window.openai.callTool('say_hello', {
                        input: {
                            name: name,
                            emoji: emoji
                        }
                    });

                    // Mostrar el resultado
                    // result.content es un array, tomamos el primer elemento
                    const greeting = result.content[0].text;
                    resultDiv.textContent = greeting;
                    resultDiv.className = 'result show';

                } catch (error) {
                    // Manejar errores
                    console.error('Error al llamar say_hello:', error);
                    resultDiv.textContent = `❌ Error: ${error.message}`;
                    resultDiv.className = 'result show error';

                } finally {
                    // Re-habilitar botón
                    button.disabled = false;
                    button.textContent = 'Saludar';
                }
            }
        </script>
    </body>
    </html>
    """
    return html
```

**Qué hace esto:**

**JavaScript mejorado**:
- `async function greet()`: Función asíncrona (porque `callTool` retorna Promise)
- `window.openai.callTool('say_hello', {...})`: Llama la herramienta MCP
- `input: { name: name, emoji: emoji }`: Argumentos envueltos en `input` (porque la herramienta espera `SayHelloInput`)
- `result.content[0].text`: Extrae el texto del resultado MCP
- `try/catch`: Manejo robusto de errores
- Estados de UI: Loading, success, error

**Estilos mejorados**:
- `.error`: Fondo rojo para errores
- `.loading`: Opacidad reducida para estado de carga
- `button:disabled`: Estilos para botón deshabilitado

### 4.3 Probar el Widget con ChatGPT

Ahora necesitamos probar el widget en ChatGPT porque `window.openai` solo existe en ese contexto.

**Paso 1: Reiniciar el servidor**

```bash
# Ctrl+C para detener
just dev
```

**Paso 2: Iniciar ngrok** (en otra terminal)

```bash
just tunnel
# O directamente:
ngrok http 8000
```

**Copia la URL de ngrok** (ej: `https://abc123.ngrok-free.app`)

**Paso 3: Actualizar PUBLIC_URL**

```bash
# Editar .env
nano .env
# O usa tu editor
```

Actualiza:
```bash
PUBLIC_URL=https://abc123.ngrok-free.app
```

**Paso 4: Reiniciar el servidor** con la nueva URL

```bash
# Ctrl+C y luego:
just dev
```

**Paso 5: Conectar desde ChatGPT**

1. Abre ChatGPT: https://chatgpt.com
2. Escribe:
   ```
   Conecta con mi servidor MCP en: https://abc123.ngrok-free.app/mcp
   ```
   (Reemplaza con tu URL de ngrok)

3. Acepta la conexión cuando ChatGPT lo solicite

**Paso 6: Solicitar el Widget**

En ChatGPT, escribe:
```
Muéstrame el widget de saludos
```

O:
```
Usa el widget hello.html
```

ChatGPT debería mostrar tu widget.

**✅ Validar en ChatGPT:**

1. **El widget se ve bien** (gradiente morado, formulario, botón)
2. **Ingresa un nombre** (ej: "Ana")
3. **Haz clic en "Saludar"**
4. **Deberías ver**:
   - Botón se deshabilita y muestra "Saludando..."
   - Mensaje de loading: "⏳ Llamando al servidor MCP..."
   - Resultado: "¡Hola Ana! 👋"

5. **Desmarca el emoji y prueba de nuevo**
   - Resultado: "¡Hola Ana!"

6. **Borra el nombre y haz clic**
   - Error: "⚠️ Por favor ingresa un nombre"

Si todo funciona, ¡tu widget está 100% integrado con MCP! ✅

### 4.4 Verificar en los Logs del Servidor

Mientras usas el widget en ChatGPT, observa los logs del servidor:

```bash
# En la terminal donde corre `just dev` deberías ver:
INFO: 127.0.0.1:xxxxx - "POST /mcp HTTP/1.1" 200 OK
Processing request of type CallToolRequest
Tool called: say_hello with arguments: {'input': {'name': 'Ana', 'emoji': True}}
```

Esto confirma que el widget está llamando correctamente a tu herramienta MCP.

🎓 **Aprendiste:**
- Cómo usar `window.openai.callTool()` para llamar herramientas MCP
- Manejar Promises con `async/await` en JavaScript
- Estructura de argumentos para herramientas (objeto `input`)
- Extraer resultados de respuestas MCP (`result.content[0].text`)
- Manejo robusto de errores con `try/catch/finally`
- Estados de UI (loading, success, error)
- El flujo completo: Widget → ChatGPT → MCP → Servidor → Respuesta → Widget

---

## Parte 5: Widget Final Pulido

### 5.1 Mejoras de UX

Vamos a agregar los toques finales para una mejor experiencia de usuario:

**Características a agregar**:
1. Historial de saludos
2. Animaciones suaves
3. Teclado (presionar Enter para saludar)
4. Limpiar input después de saludar
5. Contador de saludos

### 5.2 Widget Final Completo

**Actualizar `hello_widget()` con la versión final**:

```python
@mcp.resource("ui://widget/hello.html")
def hello_widget() -> str:
    """Widget HTML para saludar personas."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Widget de Saludos</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }

            .container {
                max-width: 500px;
                margin: 0 auto;
            }

            h1 {
                font-size: 2em;
                margin-bottom: 10px;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            .subtitle {
                text-align: center;
                opacity: 0.9;
                margin-bottom: 30px;
                font-size: 0.9em;
            }

            .form-group {
                margin-bottom: 15px;
            }

            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                font-size: 0.9em;
            }

            input[type="text"] {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                transition: box-shadow 0.3s;
            }

            input[type="text"]:focus {
                outline: none;
                box-shadow: 0 0 0 3px rgba(255,255,255,0.5);
            }

            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
            }

            input[type="checkbox"] {
                width: 20px;
                height: 20px;
                cursor: pointer;
            }

            button {
                width: 100%;
                padding: 14px;
                background: white;
                color: #667eea;
                border: none;
                border-radius: 8px;
                font-size: 1.1em;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }

            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            }

            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }

            .result {
                margin-top: 20px;
                padding: 20px;
                background: rgba(255,255,255,0.2);
                border-radius: 8px;
                text-align: center;
                font-size: 1.8em;
                display: none;
                animation: fadeIn 0.5s;
            }

            .result.show {
                display: block;
            }

            .error {
                background: rgba(255,100,100,0.4);
                font-size: 1.2em;
            }

            .loading {
                opacity: 0.8;
                font-size: 1.2em;
            }

            .history {
                margin-top: 30px;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
            }

            .history h3 {
                margin-bottom: 15px;
                font-size: 1.2em;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .counter {
                background: rgba(255,255,255,0.2);
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.9em;
            }

            .history-list {
                list-style: none;
            }

            .history-item {
                padding: 10px;
                margin-bottom: 8px;
                background: rgba(255,255,255,0.1);
                border-radius: 5px;
                animation: slideIn 0.3s;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: scale(0.9); }
                to { opacity: 1; transform: scale(1); }
            }

            @keyframes slideIn {
                from { opacity: 0; transform: translateX(-20px); }
                to { opacity: 1; transform: translateX(0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👋 Widget de Saludos</h1>
            <p class="subtitle">Conectado con MCP • Powered by OpenAI Apps SDK</p>

            <div class="form-group">
                <label for="name">Nombre:</label>
                <input
                    type="text"
                    id="name"
                    placeholder="Ingresa tu nombre"
                    value="Mundo"
                    onkeypress="handleKeyPress(event)">
            </div>

            <div class="form-group">
                <div class="checkbox-group">
                    <input type="checkbox" id="emoji" checked>
                    <label for="emoji" style="margin: 0;">¿Incluir emoji?</label>
                </div>
            </div>

            <button id="greetBtn" onclick="greet()">Saludar</button>

            <div id="result" class="result"></div>

            <div class="history">
                <h3>
                    Historial de Saludos
                    <span class="counter" id="counter">0 saludos</span>
                </h3>
                <ul id="historyList" class="history-list"></ul>
            </div>
        </div>

        <script>
            let greetCount = 0;

            // Permitir enviar con Enter
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    greet();
                }
            }

            async function greet() {
                const nameInput = document.getElementById('name');
                const name = nameInput.value;
                const emoji = document.getElementById('emoji').checked;
                const resultDiv = document.getElementById('result');
                const button = document.getElementById('greetBtn');

                // Validación
                if (!name.trim()) {
                    resultDiv.textContent = '⚠️ Por favor ingresa un nombre';
                    resultDiv.className = 'result show error';
                    return;
                }

                try {
                    // UI: Loading state
                    button.disabled = true;
                    button.textContent = 'Saludando...';
                    resultDiv.textContent = '⏳ Llamando al servidor MCP...';
                    resultDiv.className = 'result show loading';

                    // Llamar herramienta MCP
                    const result = await window.openai.callTool('say_hello', {
                        input: {
                            name: name,
                            emoji: emoji
                        }
                    });

                    // Extraer saludo del resultado
                    const greeting = result.content[0].text;

                    // Mostrar resultado
                    resultDiv.textContent = greeting;
                    resultDiv.className = 'result show';

                    // Agregar al historial
                    addToHistory(greeting);

                    // Limpiar input
                    nameInput.value = '';
                    nameInput.focus();

                } catch (error) {
                    console.error('Error al llamar say_hello:', error);
                    resultDiv.textContent = `❌ Error: ${error.message}`;
                    resultDiv.className = 'result show error';

                } finally {
                    // Restaurar botón
                    button.disabled = false;
                    button.textContent = 'Saludar';
                }
            }

            function addToHistory(greeting) {
                greetCount++;

                // Actualizar contador
                const counter = document.getElementById('counter');
                counter.textContent = `${greetCount} ${greetCount === 1 ? 'saludo' : 'saludos'}`;

                // Agregar a la lista
                const historyList = document.getElementById('historyList');
                const item = document.createElement('li');
                item.className = 'history-item';
                item.textContent = greeting;

                // Insertar al inicio (más reciente arriba)
                historyList.insertBefore(item, historyList.firstChild);

                // Limitar a 5 saludos
                if (historyList.children.length > 5) {
                    historyList.removeChild(historyList.lastChild);
                }
            }
        </script>
    </body>
    </html>
    """
    return html
```

**Nuevas características**:

1. **Historial de saludos**:
   - Muestra últimos 5 saludos
   - Contador de total de saludos
   - Animaciones de slide-in

2. **UX mejorada**:
   - Presionar Enter para saludar
   - Input se limpia después de saludar
   - Focus automático en el input
   - Animaciones suaves (fadeIn, slideIn)

3. **Diseño mejorado**:
   - Subtítulo informativo
   - Sombras y transiciones
   - Hover effects en el botón
   - Estados visuales claros

### 5.3 Probar el Widget Final

**Reiniciar el servidor**:
```bash
# Ctrl+C y luego:
just dev
```

**En ChatGPT**:
1. Solicita el widget nuevamente: "Muéstrame el widget de saludos"
2. Prueba las nuevas características:
   - Ingresa varios nombres y saluda
   - Presiona Enter en vez de hacer clic
   - Observa cómo se llena el historial
   - Verifica el contador de saludos
   - Nota cómo el input se limpia automáticamente

**✅ Validar:**

- ✅ Historial muestra últimos saludos
- ✅ Contador se actualiza correctamente
- ✅ Enter funciona para saludar
- ✅ Input se limpia después de saludar
- ✅ Animaciones se ven suaves
- ✅ Máximo 5 items en historial
- ✅ Diseño se ve pulido y profesional

Si todo funciona, ¡has creado un widget MCP completo y pulido! 🎉

🎓 **Aprendiste:**
- Agregar historial y estado en widgets
- Manejar eventos de teclado (Enter)
- Manipular el DOM dinámicamente
- Limitar listas a N elementos
- Animaciones CSS para mejor UX
- Focus management para accesibilidad
- Diseño responsive y pulido

---

## 🎓 Resumen: ¿Qué Aprendiste?

### Conceptos de MCP

- ✅ **Recursos MCP**: Contenido que ChatGPT puede leer (HTML, JSON, etc.)
- ✅ **URI de widgets**: `ui://widget/*.html` para interfaces HTML
- ✅ **MIME type**: `text/html+skybridge` para widgets (aunque no necesitas especificarlo con FastMCP)
- ✅ **Protocolo**: `resources/list` y `resources/read`

### Desarrollo de Widgets

- ✅ Registrar widgets con `@mcp.resource()`
- ✅ Estructura HTML completa (DOCTYPE, head, body)
- ✅ CSS inline (sin dependencias externas)
- ✅ JavaScript para interactividad
- ✅ Formularios HTML y validación

### API window.openai

- ✅ `window.openai.callTool(name, args)`: Llamar herramientas MCP
- ✅ Manejo de Promises con `async/await`
- ✅ Estructura de argumentos: `{ input: { ... } }`
- ✅ Estructura de resultados: `result.content[0].text`
- ✅ Manejo de errores con `try/catch`

### UX y Diseño

- ✅ Estados de UI (loading, success, error)
- ✅ Animaciones CSS para transiciones suaves
- ✅ Responsive design con Flexbox
- ✅ Accesibilidad (keyboard events, focus)
- ✅ Historial y contadores
- ✅ Gradientes y sombras para profundidad

### Flujo Completo

```
Usuario interactúa con widget en ChatGPT
    ↓
JavaScript captura evento (click o Enter)
    ↓
window.openai.callTool('say_hello', {...})
    ↓
ChatGPT envía JSON-RPC al servidor MCP
    ↓
Servidor ejecuta herramienta say_hello
    ↓
Resultado vuelve a ChatGPT
    ↓
Promise se resuelve con el resultado
    ↓
JavaScript actualiza el DOM
    ↓
Usuario ve el resultado en el widget
```

---

## 🚀 Siguientes Pasos

### Nivel 1: Modificaciones Simples

**Personaliza el diseño**:
- Cambia el gradiente de colores
- Usa diferentes emojis
- Modifica las animaciones CSS

**Agrega funcionalidades**:
- Botón para limpiar historial
- Guardar historial en localStorage
- Diferentes estilos de saludo (formal/informal)

### Nivel 2: Nueva Herramienta + Widget

**Crea una herramienta `farewell`**:
```python
@mcp.tool()
def farewell(input: FarewellInput) -> str:
    """Se despide de alguien."""
    goodbye = f"¡Adiós {input.name}!"
    if input.emoji:
        goodbye += " 👋"
    return goodbye
```

**Crea un widget de despedidas** similar al de saludos.

### Nivel 3: Widget con Múltiples Herramientas

**Crea un widget que use tanto `say_hello` como `farewell`**:
- Dos botones: "Saludar" y "Despedir"
- Mismo formulario para ambos
- Historial combinado

### Nivel 4: Widget Complejo con Datos

**Explora el [Tutorial de ToDo App](./todo-app-tutorial.md)**:
- Ver widget complejo con tabla de datos
- CRUD operations desde el widget
- Integración con storage/database

---

## 🐛 Troubleshooting

### Widget No Se Muestra en ChatGPT

**Problema**: ChatGPT no muestra el widget cuando lo solicitas.

**Soluciones**:

1. **Verifica que el recurso existe**:
   ```bash
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc": "2.0", "method": "resources/list", "id": 1}' \
     2>/dev/null | grep '^data:' | sed 's/^data: //' | jq
   ```
   Debe aparecer `ui://widget/hello.html` en la lista.

2. **Verifica que ngrok está corriendo**:
   ```bash
   curl https://tu-url-ngrok.ngrok.app/
   ```
   Debe retornar `{"status": "ok", ...}`

3. **Verifica que PUBLIC_URL está configurado** (aunque no se usa en este tutorial básico):
   ```bash
   cat .env
   ```

4. **Reinicia la conexión en ChatGPT**:
   - Desconecta y vuelve a conectar con tu servidor MCP

### window.openai is undefined

**Problema**: Error en consola: `window.openai is not defined`

**Causa**: El widget se está probando fuera de ChatGPT (ej: abriendo el HTML en navegador local).

**Solución**: `window.openai` solo existe cuando el widget se renderiza en ChatGPT. Debes probar el widget en ChatGPT, no en un navegador local.

**Para desarrollo local**, puedes agregar un mock:
```javascript
// Al inicio del script
if (!window.openai) {
    window.openai = {
        callTool: async (name, args) => {
            console.log('Mock call:', name, args);
            // Simular respuesta
            return {
                content: [{
                    text: `¡Hola ${args.input.name}! 👋 (mock)`
                }]
            };
        }
    };
}
```

### Error: "Tool not found: say_hello"

**Problema**: Widget llama `callTool` pero falla con "tool not found".

**Causa**: El nombre de la herramienta no coincide.

**Solución**:

1. Verifica el nombre en `@mcp.tool()`:
   ```python
   @mcp.tool()  # Nombre será 'say_hello'
   def say_hello(input: SayHelloInput) -> str:
   ```

2. Verifica que usas el mismo nombre en `callTool`:
   ```javascript
   window.openai.callTool('say_hello', {...})
   ```

3. Lista las herramientas disponibles:
   ```bash
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
     2>/dev/null | grep '^data:' | sed 's/^data: //' | jq '.result.tools[].name'
   ```

### Widget Se Ve Roto o Sin Estilos

**Problema**: El widget se muestra pero los estilos no se aplican.

**Causas y soluciones**:

1. **HTML mal formado**:
   - Verifica que el HTML esté bien cerrado (tags `<style>`, `<script>`, etc.)
   - Usa un validador HTML online

2. **CSS con errores de sintaxis**:
   - Verifica punto y coma al final de cada declaración CSS
   - Verifica llaves abiertas/cerradas

3. **String de Python mal escapado**:
   - Si usas comillas en el HTML, asegúrate de escaparlas o usa triple quotes `"""`

### Botón "Saludar" No Hace Nada

**Problema**: Hacer clic en el botón no llama a la herramienta.

**Debugging**:

1. **Abre la consola del navegador** en ChatGPT (F12 o Cmd+Opt+I):
   - Busca errores JavaScript
   - Busca errores de red

2. **Verifica que el evento está conectado**:
   ```html
   <button onclick="greet()">Saludar</button>
   ```

3. **Verifica que la función `greet()` existe**:
   - Agrega `console.log('greet called')` al inicio de la función

4. **Verifica los argumentos de callTool**:
   ```javascript
   console.log('Calling with:', { input: { name: name, emoji: emoji } });
   const result = await window.openai.callTool('say_hello', {
       input: { name: name, emoji: emoji }
   });
   ```

### Historial No Se Actualiza

**Problema**: El historial no muestra los saludos.

**Soluciones**:

1. **Verifica que `addToHistory()` se llama**:
   ```javascript
   // En la función greet(), después de obtener el resultado
   console.log('Adding to history:', greeting);
   addToHistory(greeting);
   ```

2. **Verifica IDs del DOM**:
   ```html
   <ul id="historyList" class="history-list"></ul>
   <span class="counter" id="counter">0 saludos</span>
   ```

3. **Verifica la función `addToHistory`**:
   - Asegúrate que está definida en el `<script>`
   - Verifica que `greetCount++` incrementa correctamente

### ngrok Session Expired

**Problema**: ngrok muestra "Session Expired" después de 8 horas.

**Solución**: El plan gratuito de ngrok tiene límite de 8 horas:

1. Reinicia ngrok:
   ```bash
   # Ctrl+C para detener ngrok
   just tunnel
   ```

2. Copia la nueva URL

3. Actualiza en ChatGPT:
   ```
   Conecta con mi servidor MCP en: https://nueva-url.ngrok.app/mcp
   ```

4. NO necesitas actualizar `.env` para este tutorial (no usamos PUBLIC_URL en el widget básico)

---

## 📚 Recursos Adicionales

### Tutoriales Relacionados

- [Tutorial Hola Mundo](./hello-world-tutorial.md) - Prerequisito de este tutorial
- [Tutorial de ToDo App](./todo-app-tutorial.md) - Widget complejo con CRUD
- [Tutorial de Notes App](./notes-app-tutorial.md) - Construcción desde cero

### Documentación

- [EXPLANATION.md](../EXPLANATION.md) - Conceptos profundos de widgets
- [GUIDE.md](../GUIDE.md) - Referencia de cómo hacer widgets
- [Model Context Protocol](https://modelcontextprotocol.io/) - Especificación oficial
- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk/) - Documentación de OpenAI

### Ejemplos de Código

- `src/todo_app/mcp_server.py` líneas 134-877 - Widgets complejos de la ToDo App
- `src/todo_app/ui_components.py` - Helpers para generar HTML de widgets

---

## ✅ Checklist de Completitud

- [ ] Entiendo qué son los recursos MCP
- [ ] Sé usar `@mcp.resource()` para registrar widgets
- [ ] Sé crear HTML con CSS inline para widgets
- [ ] Entiendo `window.openai.callTool()`
- [ ] Sé manejar Promises con async/await
- [ ] Sé la estructura de argumentos para herramientas
- [ ] Sé extraer resultados de respuestas MCP
- [ ] Sé manejar errores en widgets
- [ ] He probado el widget en ChatGPT
- [ ] Entiendo el flujo completo: Widget ↔ ChatGPT ↔ MCP

---

## 🎉 ¡Felicidades!

Has completado el tutorial de widgets. Ahora sabes:

- ✅ Crear widgets HTML que ChatGPT puede mostrar
- ✅ Hacer widgets interactivos con `window.openai`
- ✅ Conectar widgets con herramientas MCP
- ✅ Manejar estado y historial en widgets
- ✅ Diseñar interfaces atractivas y responsivas
- ✅ El flujo bidireccional: UI ↔ MCP ↔ Servidor

**Estás listo para construir widgets más complejos y aplicaciones completas.** 🚀

---

**¿Qué sigue?**

→ [Tutorial de ToDo App](./todo-app-tutorial.md) - Ver widgets complejos con datos y CRUD

→ [GUIDE.md](../GUIDE.md) - Referencia para resolver problemas específicos

→ **Construye tu propia app** con herramientas y widgets personalizados!
