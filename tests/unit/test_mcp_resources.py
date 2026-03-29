"""Tests para MCP resources."""

import pytest
from pytest_httpx import HTTPXMock

from mcp_argentina.infrastructure.mcp.resources import (
    get_cotizaciones_actual,
    get_indicadores_resumen,
)


@pytest.fixture
def mock_dolarapi_response():
    """Respuesta simulada de dolarapi."""
    return [
        {
            "moneda": "USD",
            "casa": "blue",
            "nombre": "Blue",
            "compra": 1350.0,
            "venta": 1400.0,
            "fechaActualizacion": "2026-03-29T01:00:00.000Z",
        },
        {
            "moneda": "USD",
            "casa": "oficial",
            "nombre": "Oficial",
            "compra": 900.0,
            "venta": 950.0,
            "fechaActualizacion": "2026-03-29T01:00:00.000Z",
        },
        {
            "moneda": "USD",
            "casa": "mep",
            "nombre": "MEP",
            "compra": 1300.0,
            "venta": 1320.0,
            "fechaActualizacion": "2026-03-29T01:00:00.000Z",
        },
    ]


class TestGetCotizacionesActual:
    """Tests para resource cotizaciones actual."""

    @pytest.mark.asyncio
    async def test_retorna_estructura_correcta(
        self, httpx_mock: HTTPXMock, mock_dolarapi_response
    ) -> None:
        """Debe retornar estructura con timestamp, cotizaciones, resumen."""
        httpx_mock.add_response(json=mock_dolarapi_response)
        result = await get_cotizaciones_actual()
        
        assert "timestamp" in result
        assert "cotizaciones" in result
        assert "resumen" in result

    @pytest.mark.asyncio
    async def test_cotizaciones_contiene_tipos(
        self, httpx_mock: HTTPXMock, mock_dolarapi_response
    ) -> None:
        """Debe incluir cotizaciones por tipo."""
        httpx_mock.add_response(json=mock_dolarapi_response)
        result = await get_cotizaciones_actual()
        
        assert "blue" in result["cotizaciones"]
        assert "oficial" in result["cotizaciones"]
        assert "mep" in result["cotizaciones"]

    @pytest.mark.asyncio
    async def test_resumen_incluye_indicadores(
        self, httpx_mock: HTTPXMock, mock_dolarapi_response
    ) -> None:
        """Debe calcular indicadores en resumen."""
        httpx_mock.add_response(json=mock_dolarapi_response)
        result = await get_cotizaciones_actual()
        
        resumen = result["resumen"]
        assert "dolar_blue" in resumen
        assert "dolar_oficial" in resumen
        assert "brecha_porcentaje" in resumen

    @pytest.mark.asyncio
    async def test_brecha_calculada_correctamente(
        self, httpx_mock: HTTPXMock, mock_dolarapi_response
    ) -> None:
        """Debe calcular brecha correctamente."""
        httpx_mock.add_response(json=mock_dolarapi_response)
        result = await get_cotizaciones_actual()
        
        # Blue 1400, Oficial 950 -> brecha = ((1400-950)/950)*100 = 47.37%
        brecha = result["resumen"]["brecha_porcentaje"]
        assert 45 < brecha < 50  # aproximadamente 47%

    @pytest.mark.asyncio
    async def test_cotizacion_tiene_campos_esperados(
        self, httpx_mock: HTTPXMock, mock_dolarapi_response
    ) -> None:
        """Cada cotización debe tener campos necesarios."""
        httpx_mock.add_response(json=mock_dolarapi_response)
        result = await get_cotizaciones_actual()
        
        blue = result["cotizaciones"]["blue"]
        assert "compra" in blue
        assert "venta" in blue
        assert "fecha" in blue


class TestGetIndicadoresResumen:
    """Tests para resource indicadores resumen."""

    @pytest.mark.asyncio
    async def test_retorna_estructura_correcta(
        self, httpx_mock: HTTPXMock, mock_dolarapi_response
    ) -> None:
        """Debe retornar estructura con indicadores y metadata."""
        httpx_mock.add_response(json=mock_dolarapi_response)
        result = await get_indicadores_resumen()
        
        assert "timestamp" in result
        assert "indicadores" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_metadata_incluye_source(
        self, httpx_mock: HTTPXMock, mock_dolarapi_response
    ) -> None:
        """Debe incluir source en metadata."""
        httpx_mock.add_response(json=mock_dolarapi_response)
        result = await get_indicadores_resumen()
        
        assert result["metadata"]["source"] == "dolarapi.com"
        assert "version" in result["metadata"]

    @pytest.mark.asyncio
    async def test_indicadores_incluye_cotizaciones_disponibles(
        self, httpx_mock: HTTPXMock, mock_dolarapi_response
    ) -> None:
        """Debe listar cotizaciones disponibles."""
        httpx_mock.add_response(json=mock_dolarapi_response)
        result = await get_indicadores_resumen()
        
        disponibles = result["indicadores"]["cotizaciones_disponibles"]
        assert "blue" in disponibles
        assert "oficial" in disponibles
