"""
Adapter para dolarapi.com - proveedor de cotizaciones en tiempo real.
"""

from datetime import datetime
from typing import Any

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from mcp_argentina.domain.entities.cotizacion import Cotizacion
from mcp_argentina.domain.value_objects.precio import Precio


class DolarAPIAdapter:
    """
    Adapter para consultar cotizaciones desde dolarapi.com.
    
    Implementa retry automático con exponential backoff para mayor resilencia.
    """
    
    BASE_URL = "https://dolarapi.com/v1"
    TIMEOUT = 10.0
    
    def __init__(self, client: httpx.AsyncClient | None = None):
        """
        Inicializa el adapter.
        
        Args:
            client: Cliente httpx opcional. Si no se provee, se crea uno interno.
        """
        self._client = client
        self._owns_client = client is None
    
    async def __aenter__(self):
        """Context manager entry."""
        if self._owns_client:
            self._client = httpx.AsyncClient(timeout=self.TIMEOUT)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._owns_client and self._client:
            await self._client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _get(self, endpoint: str) -> dict[str, Any]:
        """
        Realiza un GET request con retry automático.
        
        Args:
            endpoint: Path relativo (ej: "/dolares/blue")
            
        Returns:
            Respuesta JSON parseada
            
        Raises:
            httpx.RequestError: Si falla después de 3 intentos
            ValueError: Si la respuesta no es válida
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async with context manager.")
        
        url = f"{self.BASE_URL}{endpoint}"
        response = await self._client.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def _parse_cotizacion(self, data: dict[str, Any]) -> Cotizacion:
        """
        Parsea un dict de respuesta a entidad Cotizacion.
        
        Args:
            data: Respuesta JSON de la API
            
        Returns:
            Entidad Cotizacion
            
        Raises:
            ValueError: Si el formato no es válido
        """
        try:
            return Cotizacion(
                moneda=data["moneda"],
                casa=data["casa"],
                nombre=data["nombre"],
                compra=Precio(valor=float(data["compra"])),
                venta=Precio(valor=float(data["venta"])),
                fecha_actualizacion=datetime.fromisoformat(
                    data["fechaActualizacion"].replace("Z", "+00:00")
                ),
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Formato de respuesta inválido: {e}") from e
    
    async def get_dolar(self, casa: str) -> Cotizacion:
        """
        Obtiene la cotización del dólar para una casa específica.
        
        Args:
            casa: Tipo de cotización (blue, oficial, mep, ccl, cripto, tarjeta)
            
        Returns:
            Cotización actual del dólar
            
        Raises:
            ValueError: Si la casa no es válida
            httpx.HTTPStatusError: Si la API devuelve error
            ConnectionError: Si falla la conexión después de reintentos
        """
        casas_validas = {"blue", "oficial", "mep", "ccl", "cripto", "tarjeta", "mayorista"}
        
        if casa not in casas_validas:
            raise ValueError(
                f"Casa '{casa}' no válida. Opciones: {', '.join(casas_validas)}"
            )
        
        try:
            data = await self._get(f"/dolares/{casa}")
            return self._parse_cotizacion(data)
        except httpx.RequestError as e:
            raise ConnectionError(f"Error al conectar con dolarapi.com: {e}") from e
    
    async def get_todas_las_cotizaciones(self) -> list[Cotizacion]:
        """
        Obtiene todas las cotizaciones disponibles del dólar.
        
        Returns:
            Lista de cotizaciones de diferentes casas
            
        Raises:
            ConnectionError: Si falla la conexión después de reintentos
        """
        try:
            data = await self._get("/dolares")
            
            if not isinstance(data, list):
                raise ValueError("Se esperaba una lista de cotizaciones")
            
            return [self._parse_cotizacion(item) for item in data]
        except httpx.RequestError as e:
            raise ConnectionError(f"Error al conectar con dolarapi.com: {e}") from e
    
    async def get_cotizacion_moneda(self, moneda: str) -> Cotizacion:
        """
        Obtiene la cotización de una moneda específica.
        
        Args:
            moneda: Código de moneda (eur, brl, etc. - lowercase)
            
        Returns:
            Cotización actual de la moneda
            
        Raises:
            ValueError: Si la moneda no es válida
            httpx.HTTPStatusError: Si la API devuelve error
            ConnectionError: Si falla la conexión después de reintentos
        """
        moneda_lower = moneda.lower()
        
        try:
            data = await self._get(f"/cotizaciones/{moneda_lower}")
            return self._parse_cotizacion(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Moneda '{moneda}' no encontrada") from e
            raise ConnectionError(f"Error al consultar moneda: {e}") from e
        except httpx.RequestError as e:
            raise ConnectionError(f"Error al conectar con dolarapi.com: {e}") from e
