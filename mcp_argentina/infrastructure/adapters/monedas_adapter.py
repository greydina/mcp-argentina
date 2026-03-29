"""
Adapter para cotizaciones de monedas extranjeras.

Soporta: EUR, BRL, UYU, CLP, y otras monedas oficiales.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import httpx


@dataclass(frozen=True)
class CotizacionMoneda:
    """Cotización de una moneda extranjera."""

    moneda: str  # Código ISO (EUR, BRL, UYU, etc.)
    nombre: str  # Nombre completo
    compra: Decimal
    venta: Decimal
    fecha_actualizacion: datetime

    @property
    def promedio(self) -> Decimal:
        """Precio promedio."""
        return (self.compra + self.venta) / 2


class MonedasAdapter:
    """
    Adapter para cotizaciones de monedas extranjeras.

    Usa dolarapi.com para obtener cotizaciones oficiales.

    Example:
        >>> adapter = MonedasAdapter()
        >>> euro = await adapter.obtener_moneda("EUR")
        >>> print(f"Euro: ${euro.venta}")
    """

    BASE_URL = "https://dolarapi.com/v1"

    MONEDAS_SOPORTADAS = {
        "EUR": "eur",
        "BRL": "brl",
        "UYU": "uyu",
        "CLP": "clp",
        "PYG": "pyg",
        "BOB": "bob",
        "COP": "cop",
        "PEN": "pen",
        "MXN": "mxn",
        "CAD": "cad",
        "GBP": "gbp",
        "JPY": "jpy",
        "CNY": "cny",
        "CHF": "chf",
        "AUD": "aud",
    }

    def __init__(self, client: httpx.AsyncClient | None = None):
        """Inicializa el adapter."""
        self._client = client
        self._owns_client = client is None

    def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea el cliente HTTP."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def obtener_moneda(self, moneda: str) -> CotizacionMoneda:
        """
        Obtiene cotización de una moneda específica.

        Args:
            moneda: Código ISO de la moneda (EUR, BRL, UYU, etc.)

        Returns:
            Cotización de la moneda

        Raises:
            ValueError: Si la moneda no está soportada
            ConnectionError: Si falla la API
        """
        moneda_upper = moneda.upper()
        if moneda_upper not in self.MONEDAS_SOPORTADAS:
            raise ValueError(
                f"Moneda '{moneda}' no soportada. "
                f"Opciones: {', '.join(self.MONEDAS_SOPORTADAS.keys())}"
            )

        endpoint = self.MONEDAS_SOPORTADAS[moneda_upper]
        url = f"{self.BASE_URL}/cotizaciones/{endpoint}"

        try:
            client = self._get_client()
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise ConnectionError(f"Error al consultar API: {e}") from e

        return self._parse_cotizacion(data, moneda_upper)

    async def obtener_todas(self) -> list[CotizacionMoneda]:
        """
        Obtiene todas las cotizaciones de monedas.

        Returns:
            Lista de cotizaciones
        """
        url = f"{self.BASE_URL}/cotizaciones"

        try:
            client = self._get_client()
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise ConnectionError(f"Error al consultar API: {e}") from e

        cotizaciones = []
        for item in data:
            moneda = item.get("moneda", "").upper()
            if moneda and moneda != "USD":  # USD se maneja por dolarapi
                try:
                    cot = self._parse_cotizacion(item, moneda)
                    cotizaciones.append(cot)
                except (ValueError, KeyError):
                    continue

        return cotizaciones

    def _parse_cotizacion(self, data: dict, moneda: str) -> CotizacionMoneda:
        """Parsea JSON a CotizacionMoneda."""
        fecha_str = data.get("fechaActualizacion", "")
        if fecha_str.endswith("Z"):
            fecha_str = fecha_str[:-1] + "+00:00"

        try:
            fecha = datetime.fromisoformat(fecha_str)
        except ValueError:
            fecha = datetime.now()

        return CotizacionMoneda(
            moneda=moneda,
            nombre=data.get("nombre", moneda),
            compra=Decimal(str(data.get("compra", 0))),
            venta=Decimal(str(data.get("venta", 0))),
            fecha_actualizacion=fecha,
        )

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._owns_client and self._client:
            await self._client.aclose()
            self._client = None
