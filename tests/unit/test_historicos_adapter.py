"""Tests para HistoricosAdapter."""

import pytest
from pytest_httpx import HTTPXMock
from datetime import date, timedelta

from mcp_argentina.infrastructure.adapters.historicos_adapter import (
    HistoricosAdapter,
    CotizacionHistorica,
)

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)


@pytest.fixture
def mock_historico_blue():
    """Mock de histórico blue."""
    hoy = date.today()
    return [
        {"casa": "blue", "compra": 1350, "venta": 1400, "fecha": (hoy - timedelta(days=2)).isoformat()},
        {"casa": "blue", "compra": 1360, "venta": 1410, "fecha": (hoy - timedelta(days=1)).isoformat()},
        {"casa": "blue", "compra": 1370, "venta": 1420, "fecha": hoy.isoformat()},
    ]


class TestHistoricosAdapter:
    """Tests del adapter de históricos."""

    @pytest.mark.asyncio
    async def test_obtener_historico_dolar(
        self, httpx_mock: HTTPXMock, mock_historico_blue
    ) -> None:
        """Debe obtener histórico de dólar."""
        httpx_mock.add_response(json=mock_historico_blue)
        
        adapter = HistoricosAdapter()
        historicos = await adapter.obtener_historico_dolar("blue", dias=7)
        
        assert len(historicos) >= 1
        assert isinstance(historicos[0], CotizacionHistorica)
        assert historicos[0].casa == "blue"

    @pytest.mark.asyncio
    async def test_historico_ordenado_por_fecha(
        self, httpx_mock: HTTPXMock, mock_historico_blue
    ) -> None:
        """Debe retornar ordenado por fecha ascendente."""
        httpx_mock.add_response(json=mock_historico_blue)
        
        adapter = HistoricosAdapter()
        historicos = await adapter.obtener_historico_dolar("blue", dias=7)
        
        for i in range(1, len(historicos)):
            assert historicos[i].fecha >= historicos[i-1].fecha

    @pytest.mark.asyncio
    async def test_tipo_invalido_falla(self, httpx_mock: HTTPXMock) -> None:
        """Debe fallar con tipo inválido."""
        adapter = HistoricosAdapter()
        
        with pytest.raises(ValueError):
            await adapter.obtener_historico_dolar("invalido")

    @pytest.mark.asyncio
    async def test_obtener_variacion_dolar(
        self, httpx_mock: HTTPXMock, mock_historico_blue
    ) -> None:
        """Debe calcular variación correctamente."""
        httpx_mock.add_response(json=mock_historico_blue)
        
        adapter = HistoricosAdapter()
        variacion = await adapter.obtener_variacion_dolar("blue", dias=7)
        
        assert "variacion_porcentual" in variacion
        assert "valor_inicio" in variacion
        assert "valor_fin" in variacion
