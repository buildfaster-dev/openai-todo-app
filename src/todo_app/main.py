"""Main MCP server application for OpenAI Apps SDK

This serves the MCP server directly following the OpenAI Apps SDK pattern.
The server exposes tools with UI widgets for ChatGPT integration.
"""

from starlette.middleware.cors import CORSMiddleware
from .mcp_server import mcp

# Get the MCP Starlette app - this is the main app
app = mcp.streamable_http_app()

# Add CORS middleware for OpenAI Apps SDK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: This server implements the MCP protocol with Streamable HTTP transport
# Tools are defined in mcp_server.py with openai/outputTemplate metadata
# Widget HTML is served via MCP resources (ui://widget/*.html URIs)
# This is the official OpenAI Apps SDK integration pattern


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
