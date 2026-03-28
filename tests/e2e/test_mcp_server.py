"""Tests end-to-end del servidor MCP completo.

Estos tests verifican el servidor completo con mocks.
"""

import pytest
from pytest_httpx import HTTPXMock

from mcp_argentina.infrastructure.mcp.server import MCPArgentinaServer


@pytest.mark.e2e
class TestMCPServerE2E:
    """Tests E2E del servidor MCP."""

    @pytest.mark.asyncio
    async def test_server_get_dolar_blue(
        self, httpx_mock: HTTPXMock, mock_dolarapi_blue_response: dict
    ) -> None:
        """Debe obtener dólar blue a través del servidor."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json=mock_dolarapi_blue_response,
        )

        server = MCPArgentinaServer()

        try:
            resultado = await server.get_dolar("blue")

            assert resultado["tipo"] == "Blue"
            assert resultado["compra"] == 950.0
            assert resultado["venta"] == 970.0
            assert resultado["promedio"] == 960.0
            assert resultado["spread"] == 20.0
            assert resultado["casa"] == "dolarapi"
            assert "fecha_actualizacion" in resultado

        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_server_get_dolar_oficial(
        self, httpx_mock: HTTPXMock, mock_dolarapi_oficial_response: dict
    ) -> None:
        """Debe obtener dólar oficial a través del servidor."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/oficial",
            json=mock_dolarapi_oficial_response,
        )

        server = MCPArgentinaServer()

        try:
            resultado = await server.get_dolar("oficial")

            assert resultado["tipo"] == "Oficial"
            assert resultado["compra"] == 800.0
            assert resultado["venta"] == 810.0

        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_server_get_cotizaciones(
        self,
        httpx_mock: HTTPXMock,
        mock_dolarapi_blue_response: dict,
        mock_dolarapi_oficial_response: dict,
    ) -> None:
        """Debe obtener todas las cotizaciones."""
        # Mock de múltiples endpoints
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/oficial",
            json=mock_dolarapi_oficial_response,
        )
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json=mock_dolarapi_blue_response,
        )
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/bolsa",
            json={
                "compra": 920.0,
                "venta": 940.0,
                "fechaActualizacion": "2024-03-28T15:30:00-03:00",
            },
        )
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/contadoconliqui",
            json={
                "compra": 930.0,
                "venta": 950.0,
                "fechaActualizacion": "2024-03-28T15:30:00-03:00",
            },
        )
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/tarjeta",
            json={
                "compra": 1000.0,
                "venta": 1020.0,
                "fechaActualizacion": "2024-03-28T15:30:00-03:00",
            },
        )
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/cripto",
            json={
                "compra": 960.0,
                "venta": 980.0,
                "fechaActualizacion": "2024-03-28T15:30:00-03:00",
            },
        )

        server = MCPArgentinaServer()

        try:
            resultado = await server.get_cotizaciones()

            assert "cotizaciones" in resultado
            assert "total" in resultado
            assert resultado["total"] == 6
            assert len(resultado["cotizaciones"]) == 6

            # Verificar estructura de cada cotización
            for cot in resultado["cotizaciones"]:
                assert "tipo" in cot
                assert "compra" in cot
                assert "venta" in cot
                assert "promedio" in cot

        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_server_get_dolar_tipo_invalido(self) -> None:
        """Debe fallar con tipo inválido."""
        server = MCPArgentinaServer()

        try:
            with pytest.raises(ValueError, match="no válido"):
                await server.get_dolar("invalido")

        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_server_get_dolar_error_http(self, httpx_mock: HTTPXMock) -> None:
        """Debe propagar errores HTTP correctamente."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            status_code=500,
        )

        server = MCPArgentinaServer()

        try:
            with pytest.raises(ConnectionError, match="Error al consultar"):
                await server.get_dolar("blue")

        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_server_cierre_limpio(
        self, httpx_mock: HTTPXMock, mock_dolarapi_blue_response: dict
    ) -> None:
        """El servidor debe cerrar recursos correctamente."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json=mock_dolarapi_blue_response,
        )

        server = MCPArgentinaServer()
        await server.get_dolar("blue")
        await server.close()

        # El cierre debe ser idempotente
        await server.close()
