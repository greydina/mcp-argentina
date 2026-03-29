"""Port para repositorio de cotizaciones."""

from abc import ABC, abstractmethod

from mcp_argentina.domain.entities.cotizacion import Cotizacion


class CotizacionRepository(ABC):
    """
    Interfaz para obtener cotizaciones de divisas e indicadores.

    Define el contrato que deben implementar los adapters de datos,
    permitiendo cambiar la fuente de datos sin modificar la lógica de negocio.
    """

    @abstractmethod
    async def obtener_dolar(self, tipo: str) -> Cotizacion:
        """
        Obtiene cotización de un tipo de dólar específico.

        Args:
            tipo: Tipo de dólar - "oficial", "blue", "mep", "ccl", "tarjeta", "cripto"

        Returns:
            Cotización del dólar solicitado con compra, venta, fecha

        Raises:
            ValueError: Si el tipo no es válido
            ConnectionError: Si falla la conexión con la fuente de datos
        """
        pass

    @abstractmethod
    async def obtener_todas(self) -> list[Cotizacion]:
        """
        Obtiene todas las cotizaciones de dólar disponibles.

        Returns:
            Lista de cotizaciones (oficial, blue, mep, ccl, etc.)

        Raises:
            ConnectionError: Si falla la conexión con la fuente de datos
        """
        pass

    @abstractmethod
    async def obtener_riesgo_pais(self) -> int:
        """
        Obtiene el valor actual del riesgo país de Argentina.

        Returns:
            Valor del riesgo país en puntos básicos (basis points)

        Raises:
            ConnectionError: Si falla la conexión con la fuente de datos
        """
        pass
