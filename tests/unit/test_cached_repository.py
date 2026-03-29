"""Tests para CachedCotizacionRepository."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp_argentina.domain.entities.cotizacion import Cotizacion
from mcp_argentina.domain.value_objects.fecha import Fecha
from mcp_argentina.domain.value_objects.precio import Precio
from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter
from mcp_argentina.infrastructure.adapters.cached_repository import CachedCotizacionRepository
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter


@pytest.fixture
def cotizacion_blue():
    """Cotización blue de ejemplo."""
    return Cotizacion(
        nombre="Blue",
        compra=Precio(valor=Decimal("1350"), moneda="ARS"),
        venta=Precio(valor=Decimal("1400"), moneda="ARS"),
        fecha_actualizacion=Fecha.ahora(),
        casa="dolarapi",
    )


@pytest.fixture
def mock_cache():
    """Mock de CacheAdapter."""
    cache = AsyncMock(spec=CacheAdapter)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.clear = AsyncMock()
    return cache


@pytest.fixture
def mock_api(cotizacion_blue):
    """Mock de DolarAPIAdapter."""
    api = AsyncMock(spec=DolarAPIAdapter)
    api.obtener_dolar = AsyncMock(return_value=cotizacion_blue)
    api.obtener_todas = AsyncMock(return_value=[cotizacion_blue])
    api.obtener_riesgo_pais = AsyncMock(return_value=1500)
    return api


class TestCachedCotizacionRepository:
    """Tests del repositorio con cache."""

    @pytest.mark.asyncio
    async def test_obtener_dolar_llama_api_si_no_hay_cache(
        self, mock_cache, mock_api, cotizacion_blue
    ) -> None:
        """Debe llamar a la API si no hay cache."""
        repo = CachedCotizacionRepository(mock_cache, mock_api)

        result = await repo.obtener_dolar("blue")

        mock_cache.get.assert_called_once_with("dolar:blue")
        mock_api.obtener_dolar.assert_called_once_with("blue")
        mock_cache.set.assert_called_once()
        assert result == cotizacion_blue

    @pytest.mark.asyncio
    async def test_obtener_dolar_usa_cache_si_existe(
        self, mock_cache, mock_api, cotizacion_blue
    ) -> None:
        """Debe usar cache si existe."""
        mock_cache.get.return_value = cotizacion_blue
        repo = CachedCotizacionRepository(mock_cache, mock_api)

        result = await repo.obtener_dolar("blue")

        mock_cache.get.assert_called_once()
        mock_api.obtener_dolar.assert_not_called()
        assert result == cotizacion_blue

    @pytest.mark.asyncio
    async def test_obtener_todas_cachea_individualmente(
        self, mock_cache, mock_api, cotizacion_blue
    ) -> None:
        """Debe cachear cada cotización individualmente."""
        repo = CachedCotizacionRepository(mock_cache, mock_api)

        await repo.obtener_todas()

        # Debe cachear la lista completa + cada item
        assert mock_cache.set.call_count >= 2

    @pytest.mark.asyncio
    async def test_obtener_riesgo_pais(self, mock_cache, mock_api) -> None:
        """Debe obtener riesgo país."""
        repo = CachedCotizacionRepository(mock_cache, mock_api)

        # El método usa httpx directo, mockear diferente
        from unittest.mock import patch

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_response = MagicMock()
            mock_response.json.return_value = {"valor": 1500}
            mock_response.raise_for_status = MagicMock()
            mock_instance.get.return_value = mock_response

            result = await repo.obtener_riesgo_pais()

        assert result == 1500

    @pytest.mark.asyncio
    async def test_invalidar_cache_tipo_especifico(self, mock_cache, mock_api) -> None:
        """Debe invalidar cache de tipo específico."""
        repo = CachedCotizacionRepository(mock_cache, mock_api)

        await repo.invalidar_cache("blue")

        mock_cache.delete.assert_called_once_with("dolar:blue")

    @pytest.mark.asyncio
    async def test_invalidar_cache_todo(self, mock_cache, mock_api) -> None:
        """Debe limpiar todo el cache."""
        repo = CachedCotizacionRepository(mock_cache, mock_api)

        await repo.invalidar_cache()

        mock_cache.clear.assert_called_once()
