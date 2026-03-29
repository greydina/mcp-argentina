#!/usr/bin/env python3
"""Script de punto de entrada para ejecutar el servidor MCP."""

import asyncio

from mcp_argentina.infrastructure.mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
