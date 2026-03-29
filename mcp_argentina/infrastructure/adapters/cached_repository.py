"""
Repositorio de cotizaciones con cache integrado.

Wrapper sobre DolarAPIAdapter que agrega caching transparente
para reducir llamadas a la API y mejorar performance.
"""

from mcp_argentina.application.ports.cotizacion_repository import CotizacionRepository
from mcp_argentina.domain.entities.cotizacion import Cotizacion
from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter


class CachedCotizacionRepository(CotizacionRepository):
    """
    Repositorio con cache para cotizaciones.

    Implementa el patrón Cache-Aside:
    1. Busca en cache
    2. Si no está, consulta API
    3. Guarda en cache
    4. Retorna resultado

    Attributes:
        cache: Adapter de cache con TTL
        api: Adapter de dolarapi.com

    Example:
        >>> cache = CacheAdapter(default_ttl=60)
        >>> api = DolarAPIAdapter()
        >>> repo = CachedCotizacionRepository(cache, api)
        >>> cot = await repo.obtener_dolar("blue")  # API call
        >>> cot = await repo.obtener_dolar("blue")  # Cache hit
    """

    def __init__(self, cache: CacheAdapter, api: DolarAPIAdapter):
        """
        Inicializa el repositorio.

        Args:
            cache: Adapter de cache
            api: Adapter de dolarapi.com
        """
        self._cache = cache
        self._api = api

    async def obtener_dolar(self, tipo: str) -> Cotizacion:
        """
        Obtiene cotización de dólar con cache.

        Args:
            tipo: Tipo de dólar (blue, oficial, mep, ccl, cripto, tarjeta)

        Returns:
            Cotización del tipo solicitado

        Raises:
            ValueError: Si el tipo no es válido
            ConnectionError: Si falla la API
        """
        cache_key = f"dolar:{tipo.lower()}"

        # Intentar obtener de cache
        cached = await self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Consultar API
        cotizacion = await self._api.obtener_dolar(tipo)

        # Guardar en cache
        await self._cache.set(cache_key, cotizacion)

        return cotizacion

    async def obtener_todas(self) -> list[Cotizacion]:
        """
        Obtiene todas las cotizaciones con cache.

        Returns:
            Lista de cotizaciones disponibles
        """
        cache_key = "dolar:todas"

        # Intentar obtener de cache
        cached = await self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Consultar API
        cotizaciones = await self._api.obtener_todas()

        # Guardar en cache
        await self._cache.set(cache_key, cotizaciones)

        # También cachear individualmente
        for cot in cotizaciones:
            await self._cache.set(f"dolar:{cot.nombre.lower()}", cot)

        return cotizaciones

    async def obtener_riesgo_pais(self) -> int:
        """
        Obtiene el riesgo país de Argentina.

        Returns:
            Valor del riesgo país en puntos

        Raises:
            ConnectionError: Si falla la API
        """
        cache_key = "riesgo_pais"

        # Intentar obtener de cache
        cached = await self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Consultar API (dolarapi tiene endpoint de riesgo país)
        import httpx

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                "https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo"
            )
            response.raise_for_status()
            data = response.json()
            riesgo = data.get("valor", 0)

        # Guardar en cache (TTL más largo para riesgo país)
        await self._cache.set(cache_key, riesgo, ttl=300)  # 5 minutos

        return riesgo

    async def invalidar_cache(self, tipo: str | None = None) -> None:
        """
        Invalida el cache.

        Args:
            tipo: Tipo específico a invalidar, o None para todo
        """
        if tipo:
            await self._cache.delete(f"dolar:{tipo.lower()}")
        else:
            await self._cache.clear()
