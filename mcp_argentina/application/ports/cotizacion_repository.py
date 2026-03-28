"""Port para repositorio de cotizaciones."""

from abc import ABC, abstractmethod

from mcp_argentina.domain.entities.cotizacion import Cotizacion


class CotizacionRepository(ABC):
    """Interfaz para obtener cotizaciones."""

    @abstractmethod
    async def obtener_dolar(self, tipo: str) -> Cotizacion:
        """Obtiene cotización de un tipo de dólar específico.

        Args:
            tipo: "oficial", "blue", "mep", "ccl", "tarjeta", "cripto"

        Returns:
            Cotización del dólar solicitado

        Raises:
            ValueError: Si el tipo no es válido
            ConnectionError: Si falla la conexión
        """
        pass

    @abstractmethod
    async def obtener_todas(self) -> list[Cotizacion]:
        """Obtiene todas las cotizaciones disponibles."""
        pass
