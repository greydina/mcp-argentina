"""
Punto de entrada para ejecutar el servidor MCP.

Uso:
    python -m mcp_argentina

O como script:
    mcp-argentina
"""

import asyncio

from mcp_argentina.infrastructure.mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
