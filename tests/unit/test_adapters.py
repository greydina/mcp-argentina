"""Tests de adapters con mocks."""

from decimal import Decimal

import httpx
import pytest
from pytest_httpx import HTTPXMock

from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter
from mcp_argentina.infrastructure.errors import (
    APITimeoutError,
    APIUnavailableError,
    InvalidCotizacionError,
)


class TestDolarAPIAdapter:
    """Tests para DolarAPIAdapter con mocks."""

    @pytest.mark.asyncio
    async def test_obtener_dolar_blue_exitoso(
        self, httpx_mock: HTTPXMock, mock_dolarapi_blue_response: dict
    ) -> None:
        """Debe obtener dólar blue exitosamente."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json=mock_dolarapi_blue_response,
        )

        adapter = DolarAPIAdapter()
        cotizacion = await adapter.obtener_dolar("blue")

        assert cotizacion.nombre == "Blue"
        assert cotizacion.compra.valor == Decimal("950.0")
        assert cotizacion.venta.valor == Decimal("970.0")
        assert cotizacion.casa == "dolarapi"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_dolar_oficial_exitoso(
        self, httpx_mock: HTTPXMock, mock_dolarapi_oficial_response: dict
    ) -> None:
        """Debe obtener dólar oficial exitosamente."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/oficial",
            json=mock_dolarapi_oficial_response,
        )

        adapter = DolarAPIAdapter()
        cotizacion = await adapter.obtener_dolar("oficial")

        assert cotizacion.nombre == "Oficial"
        assert cotizacion.compra.valor == Decimal("800.0")
        assert cotizacion.venta.valor == Decimal("810.0")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_dolar_tipo_invalido(self) -> None:
        """Debe fallar con tipo inválido."""
        adapter = DolarAPIAdapter()

        with pytest.raises(InvalidCotizacionError):
            await adapter.obtener_dolar("invalido")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_dolar_error_http(self, httpx_mock: HTTPXMock) -> None:
        """Debe manejar errores HTTP correctamente."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            status_code=500,
        )

        adapter = DolarAPIAdapter()

        with pytest.raises(APIUnavailableError):
            await adapter.obtener_dolar("blue")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_dolar_timeout(self, httpx_mock: HTTPXMock) -> None:
        """Debe manejar timeouts correctamente."""
        httpx_mock.add_exception(httpx.TimeoutException("Timeout"))

        adapter = DolarAPIAdapter()

        with pytest.raises(APITimeoutError):
            await adapter.obtener_dolar("blue")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_todas_exitoso(
        self,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Debe obtener todas las cotizaciones exitosamente."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares",
            json=[
                {
                    "nombre": "Blue",
                    "compra": 950.0,
                    "venta": 970.0,
                    "fechaActualizacion": "2024-03-28T15:30:00-03:00",
                    "casa": "dolarapi",
                },
                {
                    "nombre": "Oficial",
                    "compra": 800.0,
                    "venta": 810.0,
                    "fechaActualizacion": "2024-03-28T15:30:00-03:00",
                    "casa": "dolarapi",
                },
            ],
        )

        adapter = DolarAPIAdapter()
        cotizaciones = await adapter.obtener_todas()

        assert len(cotizaciones) == 2
        assert cotizaciones[0].nombre == "Blue"
        assert cotizaciones[1].nombre == "Oficial"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_mapeo_tipos_correcto(self, httpx_mock: HTTPXMock) -> None:
        """Debe mapear tipos correctamente a endpoints."""
        # MEP se mapea a "bolsa"
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/bolsa",
            json={
                "nombre": "MEP",
                "compra": 920.0,
                "venta": 940.0,
                "fechaActualizacion": "2024-03-28T15:30:00-03:00",
            },
        )

        adapter = DolarAPIAdapter()
        cotizacion = await adapter.obtener_dolar("mep")

        assert cotizacion.nombre == "MEP"
        await adapter.close()

    @pytest.mark.asyncio
    async def test_cliente_personalizado(
        self, httpx_mock: HTTPXMock, mock_dolarapi_blue_response: dict
    ) -> None:
        """Debe usar cliente HTTP personalizado."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json=mock_dolarapi_blue_response,
        )

        custom_client = httpx.AsyncClient()
        adapter = DolarAPIAdapter(client=custom_client)
        cotizacion = await adapter.obtener_dolar("blue")

        assert cotizacion is not None
        await custom_client.aclose()

    @pytest.mark.asyncio
    async def test_parse_cotizacion_con_decimales(self, httpx_mock: HTTPXMock) -> None:
        """Debe parsear cotizaciones con decimales correctamente."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json={
                "nombre": "Blue",
                "compra": 950.55,
                "venta": 970.99,
                "fechaActualizacion": "2024-03-28T15:30:00-03:00",
            },
        )

        adapter = DolarAPIAdapter()
        cotizacion = await adapter.obtener_dolar("blue")

        assert cotizacion.compra.valor == Decimal("950.55")
        assert cotizacion.venta.valor == Decimal("970.99")
        await adapter.close()

    @pytest.mark.asyncio
    async def test_context_manager(
        self, httpx_mock: HTTPXMock, mock_dolarapi_blue_response: dict
    ) -> None:
        """Debe funcionar como context manager."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json=mock_dolarapi_blue_response,
        )

        async with DolarAPIAdapter() as adapter:
            cotizacion = await adapter.obtener_dolar("blue")
            assert cotizacion.nombre == "Blue"
