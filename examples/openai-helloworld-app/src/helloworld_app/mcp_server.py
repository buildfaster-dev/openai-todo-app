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
