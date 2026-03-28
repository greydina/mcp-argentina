"""Tools MCP - definición de herramientas disponibles."""

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
import httpx


class GetDolarInput(BaseModel):
    """Input para get_dolar tool."""
    tipo: str = Field(
        description="Tipo de dólar: 'blue', 'oficial', 'mep', 'ccl', 'cripto', 'tarjeta'"
    )

    @field_validator("tipo")
    def validate_tipo(cls, v: str) -> str:
        """Valida que el tipo de dólar sea válido."""
        tipos_validos = ["blue", "oficial", "mep", "ccl", "cripto", "tarjeta"]
        if v.lower() not in tipos_validos:
            raise ValueError(
                f"Tipo de dólar inválido. Tipos válidos: {', '.join(tipos_validos)}"
            )
        return v.lower()


class ConvertirInput(BaseModel):
    """Input para convertir tool."""
    monto: float = Field(description="Monto a convertir", gt=0)
    de: str = Field(description="Moneda origen: 'ARS' o 'USD'")
    a: str = Field(description="Moneda destino: 'ARS' o 'USD'")
    tipo_cambio: str = Field(
        description="Tipo de cambio a usar: 'blue', 'oficial', 'mep', 'ccl'"
    )

    @field_validator("de", "a")
    def validate_moneda(cls, v: str) -> str:
        """Valida que la moneda sea ARS o USD."""
        if v.upper() not in ["ARS", "USD"]:
            raise ValueError("Moneda debe ser 'ARS' o 'USD'")
        return v.upper()

    @field_validator("tipo_cambio")
    def validate_tipo_cambio(cls, v: str) -> str:
        """Valida que el tipo de cambio sea válido."""
        tipos_validos = ["blue", "oficial", "mep", "ccl"]
        if v.lower() not in tipos_validos:
            raise ValueError(
                f"Tipo de cambio inválido. Tipos válidos: {', '.join(tipos_validos)}"
            )
        return v.lower()


async def get_dolar(tipo: str) -> dict[str, Any]:
    """
    Obtiene la cotización actual de un tipo específico de dólar.

    Args:
        tipo: Tipo de dólar ('blue', 'oficial', 'mep', 'ccl', 'cripto', 'tarjeta')

    Returns:
        Diccionario con:
        - compra: precio de compra
        - venta: precio de venta
        - fecha: fecha de actualización
        - tipo: tipo de dólar consultado

    Raises:
        httpx.HTTPError: Si falla la petición a la API
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

    Returns:
        Diccionario con todas las cotizaciones por tipo:
        {
            "blue": {...},
            "oficial": {...},
            "mep": {...},
            "ccl": {...},
            "cripto": {...},
            "tarjeta": {...}
        }

    Raises:
        httpx.HTTPError: Si falla la petición a la API
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://dolarapi.com/v1/dolares")
        response.raise_for_status()
        data = response.json()

        # Organizar por tipo (casa de cambio)
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


async def convertir(
    monto: float, de: str, a: str, tipo_cambio: str
) -> dict[str, Any]:
    """
    Convierte un monto entre ARS y USD usando un tipo de cambio específico.

    Args:
        monto: Cantidad a convertir (debe ser > 0)
        de: Moneda origen ('ARS' o 'USD')
        a: Moneda destino ('ARS' o 'USD')
        tipo_cambio: Tipo de cambio a usar ('blue', 'oficial', 'mep', 'ccl')

    Returns:
        Diccionario con:
        - monto_original: cantidad en moneda origen
        - monto_convertido: cantidad en moneda destino
        - moneda_origen: moneda de origen
        - moneda_destino: moneda de destino
        - tipo_cambio: tipo de cambio usado
        - cotizacion_usada: cotización aplicada (compra o venta)
        - valor_cotizacion: valor numérico de la cotización

    Raises:
        ValueError: Si las monedas son iguales o el tipo de cambio no existe
        httpx.HTTPError: Si falla la petición a la API
    """
    if de == a:
        raise ValueError("La moneda origen y destino no pueden ser iguales")

    # Obtener cotización
    cotizacion = await get_dolar(tipo_cambio)

    # Determinar si usamos compra o venta
    # Si convertimos de USD a ARS, usamos venta (vendemos USD)
    # Si convertimos de ARS a USD, usamos compra (compramos USD)
    if de == "USD" and a == "ARS":
        valor = cotizacion["venta"]
        tipo_operacion = "venta"
        monto_convertido = monto * valor
    else:  # de == "ARS" and a == "USD"
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
