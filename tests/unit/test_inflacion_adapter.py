"""Tests para InflacionAdapter."""

import pytest
from pytest_httpx import HTTPXMock
from datetime import date

from mcp_argentina.infrastructure.adapters.inflacion_adapter import (
    InflacionAdapter,
    InflacionActual,
)

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)


@pytest.fixture
def mock_inflacion_historico():
    """Mock de histórico de inflación."""
    return [
        {"fecha": "2025-01-31", "valor": 2.5},
        {"fecha": "2025-02-28", "valor": 2.3},
        {"fecha": "2025-03-31", "valor": 2.1},
        {"fecha": "2025-04-30", "valor": 2.0},
        {"fecha": "2025-05-31", "valor": 1.9},
        {"fecha": "2025-06-30", "valor": 1.8},
        {"fecha": "2025-07-31", "valor": 1.7},
        {"fecha": "2025-08-31", "valor": 1.9},
        {"fecha": "2025-09-30", "valor": 2.1},
        {"fecha": "2025-10-31", "valor": 2.3},
        {"fecha": "2025-11-30", "valor": 2.5},
        {"fecha": "2025-12-31", "valor": 2.8},
        {"fecha": "2026-01-31", "valor": 2.9},
        {"fecha": "2026-02-28", "valor": 2.9},
    ]


class TestInflacionAdapter:
    """Tests del adapter de inflación."""

    @pytest.mark.asyncio
    async def test_obtener_historico(
        self, httpx_mock: HTTPXMock, mock_inflacion_historico
    ) -> None:
        """Debe obtener histórico de inflación."""
        httpx_mock.add_response(json=mock_inflacion_historico)
        
        adapter = InflacionAdapter()
        historico = await adapter.obtener_historico(meses=12)
        
        assert len(historico) <= 12
        assert all(hasattr(m, "valor") for m in historico)

    @pytest.mark.asyncio
    async def test_obtener_actual(
        self, httpx_mock: HTTPXMock, mock_inflacion_historico
    ) -> None:
        """Debe obtener inflación actual con cálculos."""
        httpx_mock.add_response(json=mock_inflacion_historico)
        
        adapter = InflacionAdapter()
        actual = await adapter.obtener_actual()
        
        assert isinstance(actual, InflacionActual)
        assert actual.mensual > 0
        assert actual.interanual > 0
        assert isinstance(actual.fecha_ultimo_dato, date)

    @pytest.mark.asyncio
    async def test_calculo_acumulada(
        self, httpx_mock: HTTPXMock, mock_inflacion_historico
    ) -> None:
        """Debe calcular inflación acumulada correctamente."""
        httpx_mock.add_response(json=mock_inflacion_historico)
        
        adapter = InflacionAdapter()
        actual = await adapter.obtener_actual()
        
        # Acumulada debe ser mayor que cualquier mes individual
        assert actual.acumulada_anio >= actual.mensual
