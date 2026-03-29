"""Tests para MCP tools."""

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from mcp_argentina.infrastructure.mcp.tools import (
    ConvertirInput,
    GetDolarInput,
    convertir,
    get_cotizaciones,
    get_dolar,
)


class TestGetDolarInput:
    """Tests para validación de input get_dolar."""

    def test_tipo_valido_blue(self) -> None:
        """Debe aceptar tipo blue."""
        inp = GetDolarInput(tipo="blue")
        assert inp.tipo == "blue"

    def test_tipo_valido_oficial(self) -> None:
        """Debe aceptar tipo oficial."""
        inp = GetDolarInput(tipo="oficial")
        assert inp.tipo == "oficial"

    def test_tipo_valido_mayusculas(self) -> None:
        """Debe normalizar a minúsculas."""
        inp = GetDolarInput(tipo="BLUE")
        assert inp.tipo == "blue"

    def test_tipo_invalido_falla(self) -> None:
        """Debe rechazar tipos inválidos."""
        with pytest.raises(ValidationError):
            GetDolarInput(tipo="inexistente")

    def test_tipos_validos_completos(self) -> None:
        """Debe aceptar todos los tipos válidos."""
        for tipo in ["blue", "oficial", "mep", "ccl", "cripto", "tarjeta"]:
            inp = GetDolarInput(tipo=tipo)
            assert inp.tipo == tipo


class TestConvertirInput:
    """Tests para validación de input convertir."""

    def test_conversion_valida(self) -> None:
        """Debe aceptar conversión válida."""
        inp = ConvertirInput(
            monto=100.0,
            de="ARS",
            a="USD",
            tipo_cambio="blue",
        )
        assert inp.monto == 100.0
        assert inp.de == "ARS"
        assert inp.a == "USD"
        assert inp.tipo_cambio == "blue"

    def test_monto_negativo_falla(self) -> None:
        """Debe rechazar montos negativos."""
        with pytest.raises(ValidationError):
            ConvertirInput(monto=-100, de="ARS", a="USD", tipo_cambio="blue")

    def test_monto_cero_falla(self) -> None:
        """Debe rechazar monto cero."""
        with pytest.raises(ValidationError):
            ConvertirInput(monto=0, de="ARS", a="USD", tipo_cambio="blue")

    def test_moneda_invalida_falla(self) -> None:
        """Debe rechazar monedas inválidas."""
        with pytest.raises(ValidationError):
            ConvertirInput(monto=100, de="EUR", a="USD", tipo_cambio="blue")

    def test_tipo_cambio_invalido_falla(self) -> None:
        """Debe rechazar tipos de cambio inválidos."""
        with pytest.raises(ValidationError):
            ConvertirInput(monto=100, de="ARS", a="USD", tipo_cambio="invalido")

    def test_normaliza_monedas_mayusculas(self) -> None:
        """Debe normalizar monedas a mayúsculas."""
        inp = ConvertirInput(monto=100, de="ars", a="usd", tipo_cambio="blue")
        assert inp.de == "ARS"
        assert inp.a == "USD"


class TestGetDolar:
    """Tests para el tool get_dolar."""

    @pytest.mark.asyncio
    async def test_get_dolar_blue_retorna_dict(self) -> None:
        """Debe retornar diccionario con datos."""
        mock_response = {
            "moneda": "USD",
            "casa": "blue",
            "nombre": "Blue",
            "compra": 1350.0,
            "venta": 1400.0,
            "fechaActualizacion": "2026-03-29T01:00:00.000Z",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_response,
            )

            result = await get_dolar("blue")

        assert isinstance(result, dict)
        assert "tipo" in result or "casa" in result or "compra" in result


class TestGetCotizaciones:
    """Tests para el tool get_cotizaciones."""

    @pytest.mark.asyncio
    async def test_get_cotizaciones_retorna_dict(self) -> None:
        """Debe retornar diccionario con lista."""
        mock_response = [
            {"moneda": "USD", "casa": "blue", "compra": 1350, "venta": 1400},
            {"moneda": "USD", "casa": "oficial", "compra": 900, "venta": 950},
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_response,
            )

            result = await get_cotizaciones()

        assert isinstance(result, dict)


class TestConvertir:
    """Tests para el tool convertir."""

    @pytest.mark.asyncio
    async def test_convertir_ars_a_usd(self) -> None:
        """Debe convertir ARS a USD."""
        mock_response = {
            "moneda": "USD",
            "casa": "blue",
            "compra": 1350.0,
            "venta": 1400.0,
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_response,
            )

            result = await convertir(
                monto=14000,
                de="ARS",
                a="USD",
                tipo_cambio="blue",
            )

        assert isinstance(result, dict)
        assert "monto_convertido" in result or "moneda_destino" in result
