"""
Tools MCP - Modelos de input y funciones de ayuda.

Este módulo contiene los schemas Pydantic para validación de inputs
de los tools. La implementación real está en server.py.

NOTA: Este archivo se mantiene por compatibilidad con tests existentes.
La implementación principal está en server.py usando el SDK MCP.
"""

from typing import Any

import httpx
from pydantic import BaseModel, Field, field_validator

# ============================================================================
# INPUT SCHEMAS
# ============================================================================


class GetDolarInput(BaseModel):
    """
    Schema de validación para get_dolar tool.

    Attributes:
        tipo: Tipo de dólar a consultar
    """

    tipo: str = Field(
        description="Tipo de dólar: 'blue', 'oficial', 'mep', 'ccl', 'cripto', 'tarjeta'"
    )

    @field_validator("tipo")
    @classmethod
    def validate_tipo(cls, v: str) -> str:
        """Valida que el tipo de dólar sea válido."""
        tipos_validos = ["blue", "oficial", "mep", "ccl", "cripto", "tarjeta", "mayorista"]
        if v.lower() not in tipos_validos:
            raise ValueError(f"Tipo de dólar inválido. Tipos válidos: {', '.join(tipos_validos)}")
        return v.lower()


class ConvertirInput(BaseModel):
    """
    Schema de validación para convertir tool.

    Attributes:
        monto: Cantidad a convertir
        de: Moneda origen
        a: Moneda destino
        tipo_cambio: Tipo de cambio a usar
    """

    monto: float = Field(description="Monto a convertir", gt=0)
    de: str = Field(description="Moneda origen: 'ARS' o 'USD'")
    a: str = Field(description="Moneda destino: 'ARS' o 'USD'")
    tipo_cambio: str = Field(description="Tipo de cambio a usar: 'blue', 'oficial', 'mep', 'ccl'")

    @field_validator("de", "a")
    @classmethod
    def validate_moneda(cls, v: str) -> str:
        """Valida que la moneda sea ARS o USD."""
        if v.upper() not in ["ARS", "USD"]:
            raise ValueError("Moneda debe ser 'ARS' o 'USD'")
        return v.upper()

    @field_validator("tipo_cambio")
    @classmethod
    def validate_tipo_cambio(cls, v: str) -> str:
        """Valida que el tipo de cambio sea válido."""
        tipos_validos = ["blue", "oficial", "mep", "ccl"]
        if v.lower() not in tipos_validos:
            raise ValueError(f"Tipo de cambio inválido. Tipos válidos: {', '.join(tipos_validos)}")
        return v.lower()


# ============================================================================
# FUNCIONES LEGACY (para compatibilidad con tests)
# ============================================================================


async def get_dolar(tipo: str) -> dict[str, Any]:
    """
    Obtiene la cotización actual de un tipo específico de dólar.

    DEPRECATED: Usar server.py call_tool() en su lugar.
    Se mantiene para compatibilidad con tests existentes.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"https://dolarapi.com/v1/dolares/{tipo}")
        response.raise_for_status()
        data = response.json()

        return {
            "tipo": tipo,
            "compra": data.get("compra"),
            "venta": data.get("venta"),
            "fecha": data.get("fechaActualizacion"),
            "nombre": data.get("nombre"),
        }


async def get_cotizaciones() -> dict[str, Any]:
    """
    Obtiene todas las cotizaciones de dólar disponibles.

    DEPRECATED: Usar server.py call_tool() en su lugar.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://dolarapi.com/v1/dolares")
        response.raise_for_status()
        data = response.json()

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

        return cotizaciones


async def convertir(monto: float, de: str, a: str, tipo_cambio: str) -> dict[str, Any]:
    """
    Convierte un monto entre ARS y USD.

    DEPRECATED: Usar server.py call_tool() en su lugar.
    """
    if de == a:
        raise ValueError("La moneda origen y destino no pueden ser iguales")

    cotizacion = await get_dolar(tipo_cambio)

    if de == "USD" and a == "ARS":
        valor = cotizacion["venta"]
        tipo_operacion = "venta"
        monto_convertido = monto * valor
    else:
        valor = cotizacion["compra"]
        tipo_operacion = "compra"
        monto_convertido = monto / valor

    return {
        "monto_original": round(monto, 2),
        "monto_convertido": round(monto_convertido, 2),
        "moneda_origen": de,
        "moneda_destino": a,
        "tipo_cambio": tipo_cambio,
        "cotizacion_usada": tipo_operacion,
        "valor_cotizacion": valor,
        "fecha_cotizacion": cotizacion["fecha"],
    }
