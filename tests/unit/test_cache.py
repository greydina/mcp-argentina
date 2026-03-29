"""Tests para CacheAdapter."""

import asyncio
import pytest
from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter


@pytest.fixture
def cache() -> CacheAdapter:
    """Cache con TTL corto para tests."""
    return CacheAdapter(default_ttl=1)


class TestCacheAdapter:
    """Tests del adaptador de cache."""

    @pytest.mark.asyncio
    async def test_set_y_get_valor(self, cache: CacheAdapter) -> None:
        """Debe guardar y recuperar un valor."""
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_clave_inexistente_retorna_none(self, cache: CacheAdapter) -> None:
        """Debe retornar None para claves que no existen."""
        result = await cache.get("no_existe")
        assert result is None

    @pytest.mark.asyncio
    async def test_valor_expira_despues_de_ttl(self, cache: CacheAdapter) -> None:
        """Debe expirar valores después del TTL."""
        await cache.set("key_expira", "valor")
        await asyncio.sleep(1.1)  # Esperar más que TTL
        result = await cache.get("key_expira")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_elimina_valor(self, cache: CacheAdapter) -> None:
        """Debe eliminar valores con delete."""
        await cache.set("key_delete", "valor")
        await cache.delete("key_delete")
        result = await cache.get("key_delete")
        assert result is None

    @pytest.mark.asyncio
    async def test_clear_elimina_todo(self, cache: CacheAdapter) -> None:
        """Debe limpiar todo el cache."""
        await cache.set("k1", "v1")
        await cache.set("k2", "v2")
        await cache.clear()
        assert await cache.get("k1") is None
        assert await cache.get("k2") is None

    @pytest.mark.asyncio
    async def test_valor_existe_despues_de_set(self, cache: CacheAdapter) -> None:
        """Debe poder verificar existencia via get."""
        await cache.set("existe", "si")
        assert await cache.get("existe") is not None
        assert await cache.get("no_existe") is None

    @pytest.mark.asyncio
    async def test_sobrescribir_valor(self, cache: CacheAdapter) -> None:
        """Debe sobrescribir valor existente."""
        await cache.set("key", "original")
        await cache.set("key", "nuevo")
        result = await cache.get("key")
        assert result == "nuevo"

    @pytest.mark.asyncio
    async def test_multiples_claves(self, cache: CacheAdapter) -> None:
        """Debe manejar múltiples claves independientes."""
        await cache.set("k1", "v1")
        await cache.set("k2", "v2")
        await cache.set("k3", "v3")
        assert await cache.get("k1") == "v1"
        assert await cache.get("k2") == "v2"
        assert await cache.get("k3") == "v3"
