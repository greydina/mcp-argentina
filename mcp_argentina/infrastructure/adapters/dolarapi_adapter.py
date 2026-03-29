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
    """
    Implementación del repositorio usando dolarapi.com.
    
    API gratuita y sin autenticación que provee cotizaciones
    del dólar en Argentina en tiempo real.
    
    Endpoints utilizados:
        - GET /v1/dolares/{tipo} - Cotización específica
        - GET /v1/dolares - Todas las cotizaciones
        - GET /v1/ambito/riesgo-pais - Riesgo país
    
    Example:
        >>> async with DolarAPIAdapter() as adapter:
        ...     blue = await adapter.obtener_dolar("blue")
        ...     print(f"Blue: ${blue.venta.valor}")
    """

    BASE_URL = "https://dolarapi.com/v1"
    
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

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
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
            tipo: Tipo de dólar (oficial, blue, mep, ccl, tarjeta, cripto)
        
        Returns:
            Cotizacion con datos actualizados
        
        Raises:
            ValueError: Si el tipo no es válido
            ConnectionError: Si falla la API
        """
        tipo_lower = tipo.lower()
        
        if tipo_lower not in self.TIPO_MAP:
            raise ValueError(
                f"Tipo '{tipo}' no válido. Opciones: {', '.join(self.TIPO_MAP.keys())}"
            )

        endpoint = self.TIPO_MAP[tipo_lower]
        url = f"{self.BASE_URL}/dolares/{endpoint}"

        try:
            client = self._get_client()
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Timeout al consultar dolarapi: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"Error HTTP {e.response.status_code}: {e}") from e
        except httpx.HTTPError as e:
            raise ConnectionError(f"Error al consultar dolarapi: {e}") from e

        return self._parse_cotizacion(data, tipo_lower)

    async def obtener_todas(self) -> list[Cotizacion]:
        """
        Obtiene todas las cotizaciones disponibles.
        
        Returns:
            Lista de cotizaciones
        """
        cotizaciones = []

        for tipo in self.TIPO_MAP.keys():
            try:
                cot = await self.obtener_dolar(tipo)
                cotizaciones.append(cot)
            except (ValueError, ConnectionError):
                # Skip si falla alguna cotización individual
                continue

        return cotizaciones

    async def obtener_riesgo_pais(self) -> int:
        """
        Obtiene el riesgo país de Argentina.
        
        Returns:
            Valor del riesgo país en puntos
        
        Raises:
            ConnectionError: Si falla la API
        """
        url = f"{self.BASE_URL}/ambito/riesgo-pais"
        
        try:
            client = self._get_client()
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return int(data.get("valor", 0))
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Timeout al consultar riesgo país: {e}") from e
        except httpx.HTTPError as e:
            raise ConnectionError(f"Error al consultar riesgo país: {e}") from e

    def _parse_cotizacion(self, data: dict, tipo: str) -> Cotizacion:
        """
        Parsea JSON de dolarapi a entidad Cotizacion.
        
        Args:
            data: JSON response de la API
            tipo: Tipo de dólar consultado
        
        Returns:
            Entidad Cotizacion
        """
        # Capitalizar nombre para display
        nombre = tipo.upper() if tipo in ("mep", "ccl") else tipo.capitalize()
        
        return Cotizacion(
            nombre=nombre,
            compra=Precio(valor=Decimal(str(data["compra"])), moneda="ARS"),
            venta=Precio(valor=Decimal(str(data["venta"])), moneda="ARS"),
            fecha_actualizacion=Fecha.desde_iso(data["fechaActualizacion"]),
            casa="dolarapi",
        )

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._owns_client and self._client:
            await self._client.aclose()
            self._client = None
