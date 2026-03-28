"""
Interface abstracta para repositorios de cotizaciones.
"""

from datetime import datetime
from typing import Protocol

from mcp_argentina.domain.entities.cotizacion import Cotizacion


class CotizacionRepository(Protocol):
    """
    Protocolo para repositorios de cotizaciones.
    
    Define los métodos que debe implementar cualquier adapter
    que provea cotizaciones de monedas.
    """
    
    async def get_dolar(self, casa: str) -> Cotizacion:
        """
        Obtiene la cotización del dólar para una casa específica.
        
        Args:
            casa: Tipo de cotización (blue, oficial, mep, ccl, cripto, tarjeta)
            
        Returns:
            Cotización actual del dólar
            
        Raises:
            ValueError: Si la casa no es válida
            ConnectionError: Si falla la conexión al proveedor
        """
        ...
    
    async def get_todas_las_cotizaciones(self) -> list[Cotizacion]:
        """
        Obtiene todas las cotizaciones disponibles del dólar.
        
        Returns:
            Lista de cotizaciones de diferentes casas
            
        Raises:
            ConnectionError: Si falla la conexión al proveedor
        """
        ...
    
    async def get_cotizacion_moneda(self, moneda: str) -> Cotizacion:
        """
        Obtiene la cotización de una moneda específica.
        
        Args:
            moneda: Código de moneda (EUR, BRL, etc.)
            
        Returns:
            Cotización actual de la moneda
            
        Raises:
            ValueError: Si la moneda no es válida
            ConnectionError: Si falla la conexión al proveedor
        """
        ...
