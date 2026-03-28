"""Port para repositorio de indicadores."""

from abc import ABC, abstractmethod

from mcp_argentina.domain.entities.indicador import Indicador


class IndicadorRepository(ABC):
    """Interfaz para obtener indicadores económicos."""

    @abstractmethod
    async def obtener_riesgo_pais(self) -> Indicador:
        """Obtiene el riesgo país actual."""
        pass

    @abstractmethod
    async def obtener_inflacion(self, periodo: str = "mensual") -> Indicador:
        """Obtiene inflación según período.

        Args:
            periodo: "mensual", "anual", "acumulada"
        """
        pass
