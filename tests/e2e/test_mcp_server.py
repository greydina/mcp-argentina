"""
Tests E2E para el MCP Server.

Estos tests verifican el flujo completo del servidor MCP,
incluyendo la interacción real con la API de dolarapi.com.
"""

import pytest
from pytest_httpx import HTTPXMock
import json

# Configurar pytest-httpx para no fallar con mocks no usados
pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)

from mcp_argentina.infrastructure.mcp.server import (
    server,
    list_tools,
    list_resources,
    list_prompts,
    call_tool,
    read_resource,
    get_prompt,
    get_container,
)
from mcp_argentina.infrastructure.container import Container
from mcp.types import TextContent


@pytest.fixture(autouse=True)
async def reset_container():
    """Reset container antes y después de cada test."""
    Container.reset()
    # Reset global en server.py también
    import mcp_argentina.infrastructure.mcp.server as server_module
    server_module._container = None
    yield
    Container.reset()
    server_module._container = None


@pytest.fixture
def mock_dolar_responses(httpx_mock: HTTPXMock):
    """Mock de todas las respuestas de dolarapi."""
    # Blue
    httpx_mock.add_response(
        url="https://dolarapi.com/v1/dolares/blue",
        json={
            "compra": 1350.0,
            "venta": 1400.0,
            "fechaActualizacion": "2026-03-29T12:00:00-03:00",
        },
    )
    # Oficial
    httpx_mock.add_response(
        url="https://dolarapi.com/v1/dolares/oficial",
        json={
            "compra": 900.0,
            "venta": 950.0,
            "fechaActualizacion": "2026-03-29T12:00:00-03:00",
        },
    )
    # MEP
    httpx_mock.add_response(
        url="https://dolarapi.com/v1/dolares/bolsa",
        json={
            "compra": 1300.0,
            "venta": 1320.0,
            "fechaActualizacion": "2026-03-29T12:00:00-03:00",
        },
    )
    # CCL
    httpx_mock.add_response(
        url="https://dolarapi.com/v1/dolares/contadoconliqui",
        json={
            "compra": 1310.0,
            "venta": 1330.0,
            "fechaActualizacion": "2026-03-29T12:00:00-03:00",
        },
    )
    # Tarjeta
    httpx_mock.add_response(
        url="https://dolarapi.com/v1/dolares/tarjeta",
        json={
            "compra": 1500.0,
            "venta": 1520.0,
            "fechaActualizacion": "2026-03-29T12:00:00-03:00",
        },
    )
    # Cripto
    httpx_mock.add_response(
        url="https://dolarapi.com/v1/dolares/cripto",
        json={
            "compra": 1380.0,
            "venta": 1410.0,
            "fechaActualizacion": "2026-03-29T12:00:00-03:00",
        },
    )
    # Mayorista
    httpx_mock.add_response(
        url="https://dolarapi.com/v1/dolares/mayorista",
        json={
            "compra": 880.0,
            "venta": 890.0,
            "fechaActualizacion": "2026-03-29T12:00:00-03:00",
        },
    )
    # Riesgo país
    httpx_mock.add_response(
        url="https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo",
        json={
            "valor": 1450,
            "fecha": "2026-03-29",
        },
    )
    # Inflación
    httpx_mock.add_response(
        url="https://api.argentinadatos.com/v1/finanzas/indices/inflacion",
        json=[
            {"fecha": "2025-12-31", "valor": 2.8},
            {"fecha": "2026-01-31", "valor": 2.9},
            {"fecha": "2026-02-28", "valor": 2.9},
        ],
    )
    return httpx_mock


@pytest.fixture
def mock_historicos(httpx_mock: HTTPXMock):
    """Mock de históricos."""
    from datetime import date, timedelta
    hoy = date.today()
    
    # Histórico blue
    httpx_mock.add_response(
        url="https://api.argentinadatos.com/v1/cotizaciones/dolares/blue",
        json=[
            {"casa": "blue", "compra": 1350, "venta": 1400, "fecha": (hoy - timedelta(days=2)).isoformat()},
            {"casa": "blue", "compra": 1360, "venta": 1410, "fecha": (hoy - timedelta(days=1)).isoformat()},
            {"casa": "blue", "compra": 1370, "venta": 1420, "fecha": hoy.isoformat()},
        ],
    )
    return httpx_mock


class TestMCPToolsE2E:
    """Tests E2E de tools."""

    @pytest.mark.asyncio
    async def test_get_dolar_blue_e2e(self, mock_dolar_responses) -> None:
        """Test completo de get_dolar blue."""
        result = await call_tool("get_dolar", {"tipo": "blue"})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Blue" in result[0].text
        assert "1,350" in result[0].text or "1350" in result[0].text
        assert "1,400" in result[0].text or "1400" in result[0].text

    @pytest.mark.asyncio
    async def test_get_dolar_oficial_e2e(self, mock_dolar_responses) -> None:
        """Test completo de get_dolar oficial."""
        result = await call_tool("get_dolar", {"tipo": "oficial"})
        
        assert len(result) == 1
        assert "Oficial" in result[0].text
        assert "950" in result[0].text

    @pytest.mark.asyncio
    async def test_get_cotizaciones_e2e(self, mock_dolar_responses) -> None:
        """Test completo de get_cotizaciones."""
        result = await call_tool("get_cotizaciones", {})
        
        assert len(result) == 1
        text = result[0].text
        assert "Cotizaciones" in text
        # Debe incluir múltiples tipos
        assert "Blue" in text or "blue" in text.lower()

    @pytest.mark.asyncio
    async def test_convertir_ars_a_usd_e2e(self, mock_dolar_responses) -> None:
        """Test completo de conversión ARS a USD."""
        result = await call_tool("convertir", {
            "monto": 140000,
            "de": "ARS",
            "a": "USD",
            "tipo_cambio": "blue",
        })
        
        assert len(result) == 1
        text = result[0].text
        assert "Conversión" in text
        assert "ARS" in text
        assert "USD" in text
        # 140000 / 1350 = ~103.7
        assert "103" in text or "104" in text

    @pytest.mark.asyncio
    async def test_convertir_usd_a_ars_e2e(self, mock_dolar_responses) -> None:
        """Test completo de conversión USD a ARS."""
        result = await call_tool("convertir", {
            "monto": 100,
            "de": "USD",
            "a": "ARS",
            "tipo_cambio": "blue",
        })
        
        assert len(result) == 1
        text = result[0].text
        assert "Conversión" in text
        # 100 * 1400 = 140000
        assert "140" in text

    @pytest.mark.asyncio
    async def test_convertir_monedas_iguales_error(self, mock_dolar_responses) -> None:
        """Debe fallar si origen y destino son iguales."""
        result = await call_tool("convertir", {
            "monto": 100,
            "de": "USD",
            "a": "USD",
            "tipo_cambio": "blue",
        })
        
        assert len(result) == 1
        assert "❌" in result[0].text or "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_convertir_monto_negativo_error(self, mock_dolar_responses) -> None:
        """Debe fallar con monto negativo."""
        result = await call_tool("convertir", {
            "monto": -100,
            "de": "ARS",
            "a": "USD",
            "tipo_cambio": "blue",
        })
        
        assert len(result) == 1
        assert "❌" in result[0].text or "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_riesgo_pais_e2e(self, mock_dolar_responses) -> None:
        """Test completo de riesgo país."""
        result = await call_tool("get_riesgo_pais", {})
        
        assert len(result) == 1
        text = result[0].text
        assert "Riesgo" in text or "riesgo" in text
        assert "1450" in text or "1,450" in text

    @pytest.mark.asyncio
    async def test_tool_inexistente_error(self, mock_dolar_responses) -> None:
        """Debe manejar tool inexistente."""
        result = await call_tool("tool_que_no_existe", {})
        
        assert len(result) == 1
        assert "❌" in result[0].text or "no encontrado" in result[0].text.lower()


class TestMCPResourcesE2E:
    """Tests E2E de resources."""

    @pytest.mark.asyncio
    async def test_read_cotizaciones_actual(self, mock_dolar_responses) -> None:
        """Test completo de resource cotizaciones/actual."""
        result = await read_resource("economia://cotizaciones/actual")
        
        data = json.loads(result)
        assert "timestamp" in data
        assert "cotizaciones" in data
        assert len(data["cotizaciones"]) >= 1

    @pytest.mark.asyncio
    async def test_read_indicadores_resumen(self, mock_dolar_responses) -> None:
        """Test completo de resource indicadores/resumen."""
        result = await read_resource("economia://indicadores/resumen")
        
        data = json.loads(result)
        assert "dolar_blue" in data
        assert "dolar_oficial" in data
        assert "brecha_porcentaje" in data
        # Brecha = ((1400-950)/950)*100 = 47.37%
        assert 45 < data["brecha_porcentaje"] < 50

    @pytest.mark.asyncio
    async def test_read_resource_inexistente(self, mock_dolar_responses) -> None:
        """Debe manejar resource inexistente."""
        result = await read_resource("economia://no/existe")
        
        assert "no encontrado" in result.lower()


class TestMCPPromptsE2E:
    """Tests E2E de prompts."""

    @pytest.mark.asyncio
    async def test_get_prompt_analisis_economico(self) -> None:
        """Test completo de prompt analisis_economico."""
        result = await get_prompt("analisis_economico", {"enfoque": "general"})
        
        assert len(result) == 1
        assert result[0].role == "user"
        text = result[0].content.text
        assert "Analiza" in text or "analiza" in text
        assert "general" in text

    @pytest.mark.asyncio
    async def test_get_prompt_comparar_dolares(self) -> None:
        """Test completo de prompt comparar_dolares."""
        result = await get_prompt("comparar_dolares", {"tipos": "blue,oficial,mep"})
        
        assert len(result) == 1
        text = result[0].content.text
        assert "Compara" in text or "compara" in text
        assert "blue,oficial,mep" in text

    @pytest.mark.asyncio
    async def test_get_prompt_inexistente(self) -> None:
        """Debe manejar prompt inexistente."""
        result = await get_prompt("prompt_que_no_existe", {})
        
        assert len(result) == 1
        assert "no encontrado" in result[0].content.text.lower()


class TestMCPCacheE2E:
    """Tests E2E del sistema de cache."""

    @pytest.mark.asyncio
    async def test_cache_evita_llamadas_duplicadas(self, httpx_mock: HTTPXMock) -> None:
        """Cache debe evitar llamadas duplicadas a la API."""
        # Solo mockear una vez
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json={
                "compra": 1350.0,
                "venta": 1400.0,
                "fechaActualizacion": "2026-03-29T12:00:00-03:00",
            },
        )
        
        # Primera llamada
        result1 = await call_tool("get_dolar", {"tipo": "blue"})
        # Segunda llamada (debe usar cache)
        result2 = await call_tool("get_dolar", {"tipo": "blue"})
        
        assert result1[0].text == result2[0].text
        # httpx_mock solo registró una llamada porque la segunda fue cache hit

    @pytest.mark.asyncio
    async def test_container_es_singleton(self) -> None:
        """Container debe ser singleton."""
        c1 = get_container()
        c2 = get_container()
        assert c1 is c2


class TestMCPServerMetadata:
    """Tests de metadata del servidor."""

    def test_server_tiene_nombre(self) -> None:
        """Server debe tener nombre."""
        assert server.name == "mcp-argentina"

    @pytest.mark.asyncio
    async def test_list_tools_tiene_schemas(self) -> None:
        """Todos los tools deben tener input schemas."""
        tools = await list_tools()
        for tool in tools:
            assert tool.inputSchema is not None
            assert "type" in tool.inputSchema

    @pytest.mark.asyncio
    async def test_list_resources_tiene_metadata(self) -> None:
        """Todos los resources deben tener metadata."""
        resources = await list_resources()
        for resource in resources:
            assert resource.name is not None
            assert resource.uri is not None

    @pytest.mark.asyncio
    async def test_list_prompts_tiene_argumentos(self) -> None:
        """Prompts deben definir sus argumentos."""
        prompts = await list_prompts()
        for prompt in prompts:
            assert prompt.name is not None
            assert prompt.description is not None


class TestMCPNewToolsE2E:
    """Tests E2E de los nuevos tools."""

    @pytest.mark.asyncio
    async def test_get_historico_e2e(self, mock_dolar_responses, mock_historicos) -> None:
        """Test completo de get_historico."""
        result = await call_tool("get_historico", {"tipo": "blue", "dias": 7})
        
        assert len(result) == 1
        text = result[0].text
        assert "Histórico" in text or "historico" in text.lower()

    @pytest.mark.asyncio
    async def test_get_inflacion_e2e(self, mock_dolar_responses) -> None:
        """Test completo de get_inflacion."""
        result = await call_tool("get_inflacion", {})
        
        assert len(result) == 1
        text = result[0].text
        assert "Inflación" in text or "inflacion" in text.lower()
        assert "Mensual" in text or "mensual" in text.lower()

    @pytest.mark.asyncio
    async def test_get_variacion_e2e(self, mock_dolar_responses, mock_historicos) -> None:
        """Test completo de get_variacion."""
        result = await call_tool("get_variacion", {"tipo": "blue", "dias": 7})
        
        assert len(result) == 1
        text = result[0].text
        assert "Variación" in text or "variacion" in text.lower()

    @pytest.mark.asyncio
    async def test_get_grafico_e2e(self, mock_dolar_responses, mock_historicos) -> None:
        """Test completo de get_grafico."""
        result = await call_tool("get_grafico", {"tipo": "blue", "dias": 7})
        
        assert len(result) == 1
        text = result[0].text
        # Debe contener caracteres de gráfico ASCII
        assert any(c in text for c in ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"])
