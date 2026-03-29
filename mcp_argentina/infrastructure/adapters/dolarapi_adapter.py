"""Adapter para dolarapi.com."""

from decimal import Decimal

import httpx

from mcp_argentina.domain.entities.cotizacion import Cotizacion
from mcp_argentina.domain.value_objects.fecha import Fecha
from mcp_argentina.domain.value_objects.precio import Precio
from mcp_argentina.infrastructure.errors import (
    APIError,
    APITimeoutError,
    InvalidCotizacionError,
    NoDataError,
    handle_http_error,
)
from mcp_argentina.infrastructure.logging import LogContext, get_logger

logger = get_logger(__name__)


class DolarAPIAdapter:
    """
    Implementación del repositorio usando dolarapi.com.

    API gratuita y sin autenticación que provee cotizaciones
    del dólar en Argentina en tiempo real.

    Endpoints utilizados:
        - GET /v1/dolares/{tipo} - Cotización específica
        - GET /v1/dolares - Todas las cotizaciones

    Example:
        >>> async with DolarAPIAdapter() as adapter:
        ...     blue = await adapter.obtener_dolar("blue")
        ...     print(f"Blue: ${blue.venta.valor}")
    """

    BASE_URL = "https://dolarapi.com/v1"
    SOURCE = "dolarapi"

    # Mapeo de tipos internos a endpoints de la API
    TIPO_MAP = {
        "oficial": "oficial",
        "blue": "blue",
        "mep": "bolsa",
        "ccl": "contadoconliqui",
        "tarjeta": "tarjeta",
        "cripto": "cripto",
        "mayorista": "mayorista",
    }

    def __init__(self, client: httpx.AsyncClient | None = None):
        """
        Inicializa el adapter.

        Args:
            client: Cliente HTTP opcional (útil para tests con mocks)
        """
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "DolarAPIAdapter":
        """Context manager entry."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit."""
        if self._owns_client and self._client:
            await self._client.aclose()

    def _get_client(self) -> httpx.AsyncClient:
        """Obtiene el cliente HTTP, creándolo si es necesario."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def obtener_dolar(self, tipo: str) -> Cotizacion:
        """
        Obtiene cotización de dólar específico.

        Args:
            tipo: Tipo de dólar (blue, oficial, mep, ccl, tarjeta, cripto, mayorista)

        Returns:
            Cotizacion con los datos actuales

        Raises:
            InvalidCotizacionError: Si el tipo no es válido
            APIError: Si hay error en la API
        """
        tipo_lower = tipo.lower()
        if tipo_lower not in self.TIPO_MAP:
            raise InvalidCotizacionError(tipo, list(self.TIPO_MAP.keys()))

        endpoint = self.TIPO_MAP[tipo_lower]
        url = f"{self.BASE_URL}/dolares/{endpoint}"

        with LogContext(logger, "obtener_dolar", tipo=tipo):
            try:
                client = self._get_client()
                response = await client.get(url)

                if response.status_code != 200:
                    raise handle_http_error(self.SOURCE, response.status_code, url)

                data = response.json()
                return self._parse_cotizacion(data, tipo)

            except httpx.TimeoutException:
                raise APITimeoutError(self.SOURCE, url)
            except httpx.RequestError as e:
                raise APIError(
                    f"Error de conexión: {e}",
                    source=self.SOURCE,
                    url=url,
                )

    async def obtener_todas(self) -> list[Cotizacion]:
        """
        Obtiene todas las cotizaciones de dólar.

        Returns:
            Lista de cotizaciones

        Raises:
            APIError: Si hay error en la API
        """
        url = f"{self.BASE_URL}/dolares"

        with LogContext(logger, "obtener_todas"):
            try:
                client = self._get_client()
                response = await client.get(url)

                if response.status_code != 200:
                    raise handle_http_error(self.SOURCE, response.status_code, url)

                data = response.json()
                if not data:
                    raise NoDataError("cotizaciones", self.SOURCE)

                return [
                    self._parse_cotizacion(item, item.get("nombre", "unknown")) for item in data
                ]

            except httpx.TimeoutException:
                raise APITimeoutError(self.SOURCE, url)
            except httpx.RequestError as e:
                raise APIError(
                    f"Error de conexión: {e}",
                    source=self.SOURCE,
                    url=url,
                )

    def _parse_cotizacion(self, data: dict, tipo: str) -> Cotizacion:
        """Parsea respuesta JSON a Cotizacion."""
        return Cotizacion(
            nombre=data.get("nombre", tipo.capitalize()),
            compra=Precio(
                valor=Decimal(str(data.get("compra", 0))),
                moneda="ARS",
            ),
            venta=Precio(
                valor=Decimal(str(data.get("venta", 0))),
                moneda="ARS",
            ),
            fecha_actualizacion=Fecha.desde_iso(
                data.get("fechaActualizacion", "").replace("Z", "+00:00")
            ),
            casa=data.get("casa", self.SOURCE),
        )

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._owns_client and self._client:
            await self._client.aclose()
            self._client = None
