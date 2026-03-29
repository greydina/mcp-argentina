"""
MCP Server para datos económicos de Argentina.

Implementa el protocolo MCP usando el SDK oficial de Anthropic.
Provee tools, resources y prompts para consultar cotizaciones,
indicadores económicos y realizar conversiones.
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    ResourceTemplate,
    Prompt,
    PromptMessage,
    PromptArgument,
)

from mcp_argentina.infrastructure.container import Container


# Crear servidor MCP
server = Server("mcp-argentina")

# Container de dependencias (singleton)
_container: Container | None = None


def get_container() -> Container:
    """Obtiene o crea el container de dependencias."""
    global _container
    if _container is None:
        _container = Container()
    return _container


# ============================================================================
# TOOLS
# ============================================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lista de tools disponibles."""
    return [
        Tool(
            name="get_dolar",
            description="Obtiene la cotización actual de un tipo de dólar específico (blue, oficial, mep, ccl, cripto, tarjeta)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tipo": {
                        "type": "string",
                        "description": "Tipo de dólar: 'blue', 'oficial', 'mep', 'ccl', 'cripto', 'tarjeta'",
                        "enum": ["blue", "oficial", "mep", "ccl", "cripto", "tarjeta"],
                    }
                },
                "required": ["tipo"],
            },
        ),
        Tool(
            name="get_cotizaciones",
            description="Obtiene todas las cotizaciones de dólar disponibles en Argentina",
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
        Tool(
            name="get_riesgo_pais",
            description="Obtiene el valor actual del riesgo país de Argentina",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Ejecuta un tool."""
    container = get_container()
    
    if name == "get_dolar":
        tipo = arguments.get("tipo", "blue")
        cotizacion = await container.repository.obtener_dolar(tipo)
        result = (
            f"💵 Dólar {cotizacion.nombre}\n"
            f"Compra: ${cotizacion.compra.valor:,.2f}\n"
            f"Venta: ${cotizacion.venta.valor:,.2f}\n"
            f"Spread: ${cotizacion.spread:,.2f} ({cotizacion.spread_porcentual:.1f}%)\n"
            f"Actualizado: {cotizacion.fecha_actualizacion}"
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "get_cotizaciones":
        cotizaciones = await container.repository.obtener_todas()
        lines = ["📊 Cotizaciones actuales:\n"]
        for cot in cotizaciones:
            lines.append(
                f"• {cot.nombre}: ${cot.compra.valor:,.2f} / ${cot.venta.valor:,.2f}"
            )
        return [TextContent(type="text", text="\n".join(lines))]
    
    elif name == "convertir":
        monto = arguments["monto"]
        de = arguments["de"].upper()
        a = arguments["a"].upper()
        tipo_cambio = arguments["tipo_cambio"]
        
        if de == a:
            return [TextContent(type="text", text="❌ Moneda origen y destino no pueden ser iguales")]
        
        if monto <= 0:
            return [TextContent(type="text", text="❌ El monto debe ser mayor a 0")]
        
        cotizacion = await container.repository.obtener_dolar(tipo_cambio)
        
        if de == "USD":
            # Vendemos USD, compramos ARS
            resultado = monto * float(cotizacion.venta.valor)
            operacion = "venta"
            valor_usado = cotizacion.venta.valor
        else:
            # Compramos USD, vendemos ARS
            resultado = monto / float(cotizacion.compra.valor)
            operacion = "compra"
            valor_usado = cotizacion.compra.valor
        
        result = (
            f"💱 Conversión {de} → {a}\n"
            f"Monto original: {de} {monto:,.2f}\n"
            f"Resultado: {a} {resultado:,.2f}\n"
            f"Tipo de cambio: {tipo_cambio} ({operacion})\n"
            f"Cotización usada: ${valor_usado:,.2f}"
        )
        return [TextContent(type="text", text=result)]
    
    elif name == "get_riesgo_pais":
        riesgo = await container.repository.obtener_riesgo_pais()
        result = f"🌡️ Riesgo País Argentina: {riesgo} puntos"
        return [TextContent(type="text", text=result)]
    
    else:
        return [TextContent(type="text", text=f"❌ Tool '{name}' no encontrado")]


# ============================================================================
# RESOURCES
# ============================================================================


@server.list_resources()
async def list_resources() -> list[Resource]:
    """Lista de resources disponibles."""
    return [
        Resource(
            uri="economia://cotizaciones/actual",
            name="Cotizaciones Actuales",
            description="Snapshot de todas las cotizaciones de dólar en tiempo real",
            mimeType="application/json",
        ),
        Resource(
            uri="economia://indicadores/resumen",
            name="Resumen de Indicadores",
            description="Indicadores económicos clave de Argentina",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Lee un resource."""
    import json
    container = get_container()
    
    if uri == "economia://cotizaciones/actual":
        cotizaciones = await container.repository.obtener_todas()
        data = {
            "timestamp": str(cotizaciones[0].fecha_actualizacion) if cotizaciones else None,
            "cotizaciones": {
                cot.nombre.lower(): {
                    "compra": float(cot.compra.valor),
                    "venta": float(cot.venta.valor),
                    "spread": float(cot.spread),
                }
                for cot in cotizaciones
            },
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    elif uri == "economia://indicadores/resumen":
        cotizaciones = await container.repository.obtener_todas()
        
        # Buscar blue y oficial para calcular brecha
        blue_venta = None
        oficial_venta = None
        for cot in cotizaciones:
            if cot.nombre.lower() == "blue":
                blue_venta = float(cot.venta.valor)
            elif cot.nombre.lower() == "oficial":
                oficial_venta = float(cot.venta.valor)
        
        brecha = None
        if blue_venta and oficial_venta and oficial_venta > 0:
            brecha = round(((blue_venta - oficial_venta) / oficial_venta) * 100, 2)
        
        data = {
            "dolar_blue": blue_venta,
            "dolar_oficial": oficial_venta,
            "brecha_porcentaje": brecha,
            "cotizaciones_disponibles": [cot.nombre.lower() for cot in cotizaciones],
            "source": "dolarapi.com",
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    else:
        return f"Resource '{uri}' no encontrado"


# ============================================================================
# PROMPTS
# ============================================================================


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """Lista de prompts disponibles."""
    return [
        Prompt(
            name="analisis_economico",
            description="Genera un análisis de la situación económica argentina",
            arguments=[
                PromptArgument(
                    name="enfoque",
                    description="Área de enfoque: 'general', 'mercado_cambiario', 'brecha', 'tendencias'",
                    required=False,
                ),
            ],
        ),
        Prompt(
            name="comparar_dolares",
            description="Compara diferentes tipos de dólar y explica sus diferencias",
            arguments=[
                PromptArgument(
                    name="tipos",
                    description="Tipos a comparar separados por coma (ej: 'blue,oficial,mep')",
                    required=True,
                ),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> list[PromptMessage]:
    """Obtiene un prompt."""
    arguments = arguments or {}
    
    if name == "analisis_economico":
        enfoque = arguments.get("enfoque", "general")
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Analiza la situación económica argentina actual con enfoque en: {enfoque}

Usa los tools disponibles para obtener datos actuales:
1. Primero consulta get_cotizaciones para ver todas las cotizaciones
2. Luego analiza la brecha cambiaria
3. Finalmente da tu análisis considerando:
   - Situación del mercado cambiario
   - Qué indica la brecha blue/oficial
   - Implicancias para ahorristas y empresas

Formato: Claro, conciso, en español argentino.
Extensión: 300-500 palabras."""
                ),
            )
        ]
    
    elif name == "comparar_dolares":
        tipos = arguments.get("tipos", "blue,oficial")
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Compara los siguientes tipos de dólar: {tipos}

Para cada tipo, explica:
1. Qué es y cómo se opera
2. Cotización actual (usa get_dolar para cada uno)
3. Para qué se usa típicamente
4. Ventajas y desventajas

Termina con una recomendación de cuál usar según diferentes perfiles de usuario."""
                ),
            )
        ]
    
    else:
        return [
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=f"Prompt '{name}' no encontrado"),
            )
        ]


# ============================================================================
# MAIN
# ============================================================================


async def main():
    """Punto de entrada del servidor MCP."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
