"""MCP Server principal - punto de entrada del servidor."""

import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    Prompt,
    PromptMessage,
)

from . import tools, resources, prompts


# Crear instancia del servidor
app = Server("mcp-argentina")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Lista todas las herramientas disponibles."""
    return [
        Tool(
            name="get_dolar",
            description="Obtiene la cotización actual de un tipo específico de dólar (blue, oficial, mep, ccl, cripto, tarjeta)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tipo": {
                        "type": "string",
                        "description": "Tipo de dólar a consultar",
                        "enum": ["blue", "oficial", "mep", "ccl", "cripto", "tarjeta"],
                    }
                },
                "required": ["tipo"],
            },
        ),
        Tool(
            name="get_cotizaciones",
            description="Obtiene todas las cotizaciones de dólar disponibles en una sola llamada",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="convertir",
            description="Convierte un monto entre ARS y USD usando un tipo de cambio específico",
            inputSchema={
                "type": "object",
                "properties": {
                    "monto": {
                        "type": "number",
                        "description": "Monto a convertir (debe ser mayor a 0)",
                        "minimum": 0,
                        "exclusiveMinimum": True,
                    },
                    "de": {
                        "type": "string",
                        "description": "Moneda origen",
                        "enum": ["ARS", "USD"],
                    },
                    "a": {
                        "type": "string",
                        "description": "Moneda destino",
                        "enum": ["ARS", "USD"],
                    },
                    "tipo_cambio": {
                        "type": "string",
                        "description": "Tipo de cambio a usar",
                        "enum": ["blue", "oficial", "mep", "ccl"],
                    },
                },
                "required": ["monto", "de", "a", "tipo_cambio"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Ejecuta una herramienta."""
    try:
        if name == "get_dolar":
            result = await tools.get_dolar(arguments["tipo"])
        elif name == "get_cotizaciones":
            result = await tools.get_cotizaciones()
        elif name == "convertir":
            result = await tools.convertir(
                monto=arguments["monto"],
                de=arguments["de"],
                a=arguments["a"],
                tipo_cambio=arguments["tipo_cambio"],
            )
        else:
            raise ValueError(f"Herramienta desconocida: {name}")

        return [
            TextContent(
                type="text",
                text=str(result),
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error ejecutando {name}: {str(e)}",
            )
        ]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """Lista todos los recursos disponibles."""
    return [
        Resource(
            uri="economia://cotizaciones/actual",
            name="Cotizaciones Actuales",
            description="Snapshot de todas las cotizaciones de dólar actuales",
            mimeType="application/json",
        ),
        Resource(
            uri="economia://indicadores/resumen",
            name="Resumen de Indicadores",
            description="Resumen de indicadores económicos clave de Argentina",
            mimeType="application/json",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Lee un recurso."""
    try:
        if uri == "economia://cotizaciones/actual":
            result = await resources.get_cotizaciones_actual()
        elif uri == "economia://indicadores/resumen":
            result = await resources.get_indicadores_resumen()
        else:
            raise ValueError(f"Recurso desconocido: {uri}")

        return str(result)
    except Exception as e:
        return f"Error leyendo recurso {uri}: {str(e)}"


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """Lista todos los prompts disponibles."""
    available_prompts = prompts.list_prompts()
    
    mcp_prompts = []
    for p in available_prompts:
        prompt_data = prompts.get_prompt(p["name"])
        
        mcp_prompts.append(
            Prompt(
                name=prompt_data["name"],
                description=prompt_data["description"],
                arguments=[
                    {
                        "name": arg["name"],
                        "description": arg["description"],
                        "required": arg.get("required", False),
                    }
                    for arg in prompt_data.get("arguments", [])
                ],
            )
        )
    
    return mcp_prompts


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> list[PromptMessage]:
    """Obtiene un prompt con argumentos."""
    try:
        prompt_data = prompts.get_prompt(name)
        template = prompt_data["template"]
        
        # Rellenar template con argumentos
        if arguments:
            template = template.format(**arguments)
        else:
            # Si no hay argumentos, usar valores por defecto
            default_args = {}
            for arg in prompt_data.get("arguments", []):
                if not arg.get("required", False):
                    default_args[arg["name"]] = ""
            template = template.format(**default_args)
        
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=template,
                ),
            )
        ]
    except Exception as e:
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"Error obteniendo prompt {name}: {str(e)}",
                ),
            )
        ]


async def main():
    """Punto de entrada principal del servidor."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
