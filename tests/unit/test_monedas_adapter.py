"""Tests para MonedasAdapter."""

import pytest
from pytest_httpx import HTTPXMock

from mcp_argentina.infrastructure.adapters.monedas_adapter import (
    CotizacionMoneda,
    MonedasAdapter,
)

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)


@pytest.fixture
def mock_euro_response():
    """Mock de respuesta para EUR."""
    return {
        "moneda": "EUR",
        "nombre": "Euro",
        "compra": 1500.0,
        "venta": 1520.0,
        "fechaActualizacion": "2026-03-29T12:00:00.000Z",
    }


@pytest.fixture
def mock_todas_monedas():
    """Mock de todas las monedas."""
    return [
        {
            "moneda": "USD",
            "nombre": "Dólar",
            "compra": 950,
            "venta": 1000,
            "fechaActualizacion": "2026-03-29T12:00:00.000Z",
        },
        {
            "moneda": "EUR",
            "nombre": "Euro",
            "compra": 1500,
            "venta": 1520,
            "fechaActualizacion": "2026-03-29T12:00:00.000Z",
        },
        {
            "moneda": "BRL",
            "nombre": "Real",
            "compra": 260,
            "venta": 265,
            "fechaActualizacion": "2026-03-29T12:00:00.000Z",
        },
        {
            "moneda": "UYU",
            "nombre": "Peso Uruguayo",
            "compra": 25,
            "venta": 26,
            "fechaActualizacion": "2026-03-29T12:00:00.000Z",
        },
    ]


class TestMonedasAdapter:
    """Tests del adapter de monedas."""

    @pytest.mark.asyncio
    async def test_obtener_moneda_euro(self, httpx_mock: HTTPXMock, mock_euro_response) -> None:
        """Debe obtener cotización del euro."""
        httpx_mock.add_response(json=mock_euro_response)

        adapter = MonedasAdapter()
        euro = await adapter.obtener_moneda("EUR")

        assert isinstance(euro, CotizacionMoneda)
        assert euro.moneda == "EUR"
        assert euro.compra > 0
        assert euro.venta > 0

    @pytest.mark.asyncio
    async def test_moneda_normaliza_mayusculas(
        self, httpx_mock: HTTPXMock, mock_euro_response
    ) -> None:
        """Debe aceptar moneda en minúsculas."""
        httpx_mock.add_response(json=mock_euro_response)

        adapter = MonedasAdapter()
        euro = await adapter.obtener_moneda("eur")

        assert euro.moneda == "EUR"

    @pytest.mark.asyncio
    async def test_moneda_invalida_falla(self) -> None:
        """Debe fallar con moneda no soportada."""
        adapter = MonedasAdapter()

        with pytest.raises(ValueError, match="no soportada"):
            await adapter.obtener_moneda("XYZ")

    @pytest.mark.asyncio
    async def test_obtener_todas(self, httpx_mock: HTTPXMock, mock_todas_monedas) -> None:
        """Debe obtener todas las monedas (excepto USD)."""
        httpx_mock.add_response(json=mock_todas_monedas)

        adapter = MonedasAdapter()
        monedas = await adapter.obtener_todas()

        # No debe incluir USD
        codigos = [m.moneda for m in monedas]
        assert "USD" not in codigos
        assert "EUR" in codigos
        assert "BRL" in codigos

    @pytest.mark.asyncio
    async def test_cotizacion_tiene_promedio(
        self, httpx_mock: HTTPXMock, mock_euro_response
    ) -> None:
        """CotizacionMoneda debe calcular promedio."""
        httpx_mock.add_response(json=mock_euro_response)

        adapter = MonedasAdapter()
        euro = await adapter.obtener_moneda("EUR")

        promedio_esperado = (euro.compra + euro.venta) / 2
        assert euro.promedio == promedio_esperado
