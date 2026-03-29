"""
Resources MCP - Recursos de solo lectura.

Este módulo contiene funciones helper para resources.
La implementación MCP real está en server.py.

NOTA: Mantenido para compatibilidad con tests existentes.
"""

from typing import Any

import httpx


async def get_cotizaciones_actual() -> dict[str, Any]:
    """
    Resource: economia://cotizaciones/actual

    Proporciona un snapshot de todas las cotizaciones actuales.

    Returns:
        Diccionario con:
        - timestamp: momento de consulta
        - cotizaciones: todas las cotizaciones disponibles
        - resumen: indicadores clave
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://dolarapi.com/v1/dolares")
        response.raise_for_status()
        data = response.json()

        # Organizar cotizaciones por tipo
        cotizaciones = {}
        for item in data:
            casa = item.get("casa", "").lower()
            if casa:
                cotizaciones[casa] = {
                    "compra": item.get("compra"),
                    "venta": item.get("venta"),
                    "fecha": item.get("fechaActualizacion"),
                    "nombre": item.get("nombre"),
                }

        # Calcular resumen con indicadores clave
        resumen = {}
        if "blue" in cotizaciones:
            resumen["dolar_blue"] = cotizaciones["blue"]["venta"]
        if "oficial" in cotizaciones:
            resumen["dolar_oficial"] = cotizaciones["oficial"]["venta"]

        # Calcular brecha cambiaria
        if "dolar_blue" in resumen and "dolar_oficial" in resumen:
            oficial = resumen["dolar_oficial"]
            blue = resumen["dolar_blue"]
            if oficial and oficial > 0:
                brecha = ((blue - oficial) / oficial) * 100
                resumen["brecha_porcentaje"] = round(brecha, 2)

        return {
            "timestamp": data[0].get("fechaActualizacion") if data else None,
            "cotizaciones": cotizaciones,
            "resumen": resumen,
        }


async def get_indicadores_resumen() -> dict[str, Any]:
    """
    Resource: economia://indicadores/resumen

    Proporciona un resumen de indicadores económicos clave.

    Returns:
        Diccionario con indicadores principales y metadata.
    """
    cotizaciones_data = await get_cotizaciones_actual()

    return {
        "timestamp": cotizaciones_data["timestamp"],
        "indicadores": {
            "dolar": cotizaciones_data["resumen"],
            "cotizaciones_disponibles": list(cotizaciones_data["cotizaciones"].keys()),
        },
        "metadata": {
            "source": "dolarapi.com",
            "version": "0.1.0",
        },
    }


async def get_riesgo_pais() -> dict[str, Any]:
    """
    Resource: economia://riesgo-pais

    Proporciona el riesgo país actual de Argentina.

    Returns:
        Diccionario con valor y metadata.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://dolarapi.com/v1/ambito/riesgo-pais")
        response.raise_for_status()
        data = response.json()

        return {
            "valor": data.get("valor"),
            "fecha": data.get("fecha"),
            "source": "ambito.com",
        }
