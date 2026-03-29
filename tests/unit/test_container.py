"""Tests para Container de dependencias."""

import pytest
from mcp_argentina.infrastructure.container import Container
from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter
from mcp_argentina.infrastructure.adapters.cached_repository import CachedCotizacionRepository


class TestContainer:
    """Tests del Container de dependencias."""

    def setup_method(self) -> None:
        """Reset singleton antes de cada test."""
        Container.reset()

    def teardown_method(self) -> None:
        """Reset singleton después de cada test."""
        Container.reset()

    def test_singleton_retorna_misma_instancia(self) -> None:
        """Debe retornar la misma instancia."""
        c1 = Container()
        c2 = Container()
        assert c1 is c2

    def test_reset_crea_nueva_instancia(self) -> None:
        """Reset debe permitir crear nueva instancia."""
        c1 = Container()
        Container.reset()
        c2 = Container()
        assert c1 is not c2

    def test_tiene_cache(self) -> None:
        """Debe tener cache adapter."""
        container = Container()
        assert isinstance(container.cache, CacheAdapter)

    def test_tiene_dolarapi(self) -> None:
        """Debe tener dolarapi adapter."""
        container = Container()
        assert isinstance(container.dolarapi, DolarAPIAdapter)

    def test_tiene_repository(self) -> None:
        """Debe tener repository con cache."""
        container = Container()
        assert isinstance(container.repository, CachedCotizacionRepository)

    def test_cache_default_ttl(self) -> None:
        """Cache debe tener TTL por defecto."""
        Container.reset()
        container = Container()
        assert container.cache._default_ttl == 60  # default

    @pytest.mark.asyncio
    async def test_close_no_falla(self) -> None:
        """Close debe ejecutarse sin errores."""
        container = Container()
        await container.close()
        # No debe lanzar excepción
