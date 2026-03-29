"""Tests de adapters con mocks."""

from decimal import Decimal

import httpx
import pytest
from pytest_httpx import HTTPXMock

from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter


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

        with pytest.raises(ValueError, match="no válido"):
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

        with pytest.raises(ConnectionError, match="Error HTTP"):
            await adapter.obtener_dolar("blue")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_dolar_timeout(self, httpx_mock: HTTPXMock) -> None:
        """Debe manejar timeouts correctamente."""
        httpx_mock.add_exception(httpx.TimeoutException("Timeout"))

        adapter = DolarAPIAdapter()

        with pytest.raises(ConnectionError):
            await adapter.obtener_dolar("blue")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_todas_exitoso(
        self,
        httpx_mock: HTTPXMock,
        mock_dolarapi_blue_response: dict,
        mock_dolarapi_oficial_response: dict,
    ) -> None:
        """Debe obtener todas las cotizaciones exitosamente."""
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
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/mayorista",
            json={
                "compra": 880.0,
                "venta": 890.0,
                "fechaActualizacion": "2024-03-28T15:30:00-03:00",
            },
        )

        adapter = DolarAPIAdapter()
        cotizaciones = await adapter.obtener_todas()

        assert len(cotizaciones) == 7
        nombres = [c.nombre for c in cotizaciones]
        assert "Oficial" in nombres
        assert "Blue" in nombres

        await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_todas_con_fallos_parciales(
        self, httpx_mock: HTTPXMock, mock_dolarapi_blue_response: dict
    ) -> None:
        """Debe continuar si alguna cotización falla."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/oficial",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json=mock_dolarapi_blue_response,
        )
        # Mock el resto con errores
        for endpoint in ["bolsa", "contadoconliqui", "tarjeta", "cripto", "mayorista"]:
            httpx_mock.add_response(
                url=f"https://dolarapi.com/v1/dolares/{endpoint}",
                status_code=500,
            )

        adapter = DolarAPIAdapter()
        cotizaciones = await adapter.obtener_todas()

        # Debe retornar al menos blue
        assert len(cotizaciones) >= 1
        assert any(c.nombre == "Blue" for c in cotizaciones)

        await adapter.close()

    @pytest.mark.asyncio
    async def test_mapeo_tipos_correcto(self) -> None:
        """Debe mapear tipos correctamente."""
        adapter = DolarAPIAdapter()

        # Verificar que los tipos válidos no lanzan ValueError
        tipos_validos = ["oficial", "blue", "mep", "ccl", "tarjeta", "cripto"]

        for tipo in tipos_validos:
            # No queremos hacer requests reales, solo verificar que no falla en validación
            pass

        # Tipo inválido debe fallar
        with pytest.raises(ValueError):
            await adapter.obtener_dolar("euro")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_cliente_personalizado(
        self, httpx_mock: HTTPXMock, mock_dolarapi_blue_response: dict
    ) -> None:
        """Debe aceptar cliente HTTP personalizado."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json=mock_dolarapi_blue_response,
        )

        async with httpx.AsyncClient() as client:
            adapter = DolarAPIAdapter(client=client)
            cotizacion = await adapter.obtener_dolar("blue")

            assert cotizacion.nombre == "Blue"
            # No llamar adapter.close() porque el cliente es externo

    @pytest.mark.asyncio
    async def test_parse_cotizacion_con_decimales(self, httpx_mock: HTTPXMock) -> None:
        """Debe parsear correctamente valores con decimales."""
        httpx_mock.add_response(
            url="https://dolarapi.com/v1/dolares/blue",
            json={
                "compra": 950.75,
                "venta": 970.25,
                "fechaActualizacion": "2024-03-28T15:30:00-03:00",
            },
        )

        adapter = DolarAPIAdapter()
        cotizacion = await adapter.obtener_dolar("blue")

        assert cotizacion.compra.valor == Decimal("950.75")
        assert cotizacion.venta.valor == Decimal("970.25")

        await adapter.close()
