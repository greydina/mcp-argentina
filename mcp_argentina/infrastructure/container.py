"""
Container de dependencias para inyección de dependencias.

Centraliza la creación y configuración de todos los componentes
del sistema, facilitando testing y mantenimiento.
"""

from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter
from mcp_argentina.infrastructure.adapters.cached_repository import CachedCotizacionRepository
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter


class Container:
    """
    Container de dependencias (Singleton pattern).

    Centraliza la creación de:
    - Cache: almacenamiento en memoria con TTL
    - DolarAPI: adapter para dolarapi.com
    - Repository: repositorio con cache integrado

    Example:
        >>> container = Container()
        >>> cotizacion = await container.repository.obtener_dolar("blue")
    """

    _instance = None

    def __new__(cls):
        """Singleton: retorna instancia existente o crea nueva."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, cache_ttl: int = 60):
        """
        Inicializa el container.

        Args:
            cache_ttl: TTL del cache en segundos (default: 60)
        """
        if self._initialized:
            return

        # Componentes internos
        self._cache = CacheAdapter(default_ttl=cache_ttl)
        self._dolarapi = DolarAPIAdapter()

        # Repositorio principal con cache
        self._repository = CachedCotizacionRepository(
            cache=self._cache,
            api=self._dolarapi,
        )

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

    async def close(self) -> None:
        """Cierra todos los recursos."""
        await self._dolarapi.close()
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
