"""Adapter para dolarapi.com."""

from decimal import Decimal

import httpx

from mcp_argentina.application.ports.cotizacion_repository import (
    CotizacionRepository,
)
from mcp_argentina.domain.entities.cotizacion import Cotizacion
from mcp_argentina.domain.value_objects.fecha import Fecha
from mcp_argentina.domain.value_objects.precio import Precio


class DolarAPIAdapter(CotizacionRepository):
    """Implementación usando dolarapi.com."""

    BASE_URL = "https://dolarapi.com/v1"

    def __init__(self, client: httpx.AsyncClient | None = None):
        """Inicializa el adapter.

        Args:
            client: Cliente HTTP opcional (útil para tests)
        """
        self._client = client or httpx.AsyncClient(timeout=10.0)

    async def obtener_dolar(self, tipo: str) -> Cotizacion:
        """Obtiene cotización de dólar específico."""
        tipo_map = {
            "oficial": "oficial",
            "blue": "blue",
            "mep": "bolsa",
            "ccl": "contadoconliqui",
            "tarjeta": "tarjeta",
            "cripto": "cripto",
        }

        if tipo not in tipo_map:
            raise ValueError(
                f"Tipo '{tipo}' no válido. Opciones: {', '.join(tipo_map.keys())}"
            )

        endpoint = tipo_map[tipo]
        url = f"{self.BASE_URL}/dolares/{endpoint}"

        try:
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise ConnectionError(f"Error al consultar dolarapi: {e}") from e

        return self._parse_cotizacion(data, tipo)

    async def obtener_todas(self) -> list[Cotizacion]:
        """Obtiene todas las cotizaciones."""
        tipos = ["oficial", "blue", "mep", "ccl", "tarjeta", "cripto"]
        cotizaciones = []

        for tipo in tipos:
            try:
                cot = await self.obtener_dolar(tipo)
                cotizaciones.append(cot)
            except (ValueError, ConnectionError):
                # Skip si falla alguna cotización
                continue

        return cotizaciones

    def _parse_cotizacion(self, data: dict, tipo: str) -> Cotizacion:
        """Parsea JSON de dolarapi a Cotizacion."""
        return Cotizacion(
            nombre=tipo.capitalize(),
            compra=Precio(monto=Decimal(str(data["compra"])), moneda="ARS"),
            venta=Precio(monto=Decimal(str(data["venta"])), moneda="ARS"),
            fecha_actualizacion=Fecha.desde_iso(data["fechaActualizacion"]),
            casa="dolarapi",
        )

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        await self._client.aclose()
