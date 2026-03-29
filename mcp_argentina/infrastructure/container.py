"""
Container de dependencias para inyección de dependencias.

Centraliza la creación y configuración de todos los componentes
del sistema, facilitando testing y mantenimiento.
"""

from mcp_argentina.application.services.alertas_service import AlertasService
from mcp_argentina.application.services.graficos_service import GraficosService
from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter
from mcp_argentina.infrastructure.adapters.cached_repository import (
    CachedCotizacionRepository,
)
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter
from mcp_argentina.infrastructure.adapters.historicos_adapter import HistoricosAdapter
from mcp_argentina.infrastructure.adapters.inflacion_adapter import InflacionAdapter
from mcp_argentina.infrastructure.adapters.monedas_adapter import MonedasAdapter


class Container:
    """
    Container de dependencias (Singleton pattern).

    Centraliza la creación de todos los componentes:
    - Cache: almacenamiento en memoria con TTL
    - DolarAPI: adapter para dolarapi.com
    - Repository: repositorio con cache integrado
    - Historicos: datos históricos de cotizaciones
    - Inflacion: datos de inflación
    - Monedas: cotizaciones de otras monedas
    - Alertas: servicio de alertas
    - Graficos: generación de gráficos ASCII

    Example:
        >>> container = Container()
        >>> cotizacion = await container.repository.obtener_dolar("blue")
        >>> historicos = await container.historicos.obtener_historico_dolar("blue")
    """

    _instance: "Container | None" = None
    _initialized: bool = False

    def __new__(cls) -> "Container":
        """Singleton: retorna instancia existente o crea nueva."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, cache_ttl: int = 60) -> None:
        """
        Inicializa el container.

        Args:
            cache_ttl: TTL del cache en segundos (default: 60)
        """
        if self._initialized:
            return

        # Componentes de infraestructura
        self._cache = CacheAdapter(default_ttl=cache_ttl)
        self._dolarapi = DolarAPIAdapter()
        self._historicos = HistoricosAdapter()
        self._inflacion = InflacionAdapter()
        self._monedas = MonedasAdapter()

        # Repositorio principal con cache
        self._repository = CachedCotizacionRepository(
            cache=self._cache,
            api=self._dolarapi,
        )

        # Servicios de aplicación
        self._alertas = AlertasService(self._repository)
        self._graficos = GraficosService()

        self._initialized = True

    @property
    def cache(self) -> CacheAdapter:
        """Cache en memoria."""
        return self._cache

    @property
    def dolarapi(self) -> DolarAPIAdapter:
        """Adapter de dolarapi.com (sin cache)."""
        return self._dolarapi

    @property
    def repository(self) -> CachedCotizacionRepository:
        """Repositorio de cotizaciones con cache."""
        return self._repository

    @property
    def historicos(self) -> HistoricosAdapter:
        """Adapter de datos históricos."""
        return self._historicos

    @property
    def inflacion(self) -> InflacionAdapter:
        """Adapter de inflación."""
        return self._inflacion

    @property
    def monedas(self) -> MonedasAdapter:
        """Adapter de otras monedas."""
        return self._monedas

    @property
    def alertas(self) -> AlertasService:
        """Servicio de alertas."""
        return self._alertas

    @property
    def graficos(self) -> GraficosService:
        """Servicio de gráficos."""
        return self._graficos

    async def close(self) -> None:
        """Cierra todos los recursos."""
        await self._dolarapi.close()
        await self._historicos.close()
        await self._inflacion.close()
        await self._monedas.close()
        await self._cache.clear()

    @classmethod
    def reset(cls) -> None:
        """
        Resetea el singleton (útil para tests).

        Example:
            >>> Container.reset()
            >>> container = Container()  # Nueva instancia
        """
        cls._instance = None
