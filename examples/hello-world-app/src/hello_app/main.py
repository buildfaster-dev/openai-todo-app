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
