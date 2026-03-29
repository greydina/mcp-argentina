"""Tests de integración para MCP tools."""

import pytest

from mcp_argentina.infrastructure.mcp import tools


@pytest.mark.asyncio
async def test_get_dolar_blue():
    """Test obtener cotización del dólar blue."""
    result = await tools.get_dolar("blue")

    assert result is not None
    assert "tipo" in result
    assert result["tipo"] == "blue"
    assert "compra" in result
    assert "venta" in result
    assert result["compra"] is not None
    assert result["venta"] is not None
    assert result["venta"] >= result["compra"]


@pytest.mark.asyncio
async def test_get_dolar_oficial():
    """Test obtener cotización del dólar oficial."""
    result = await tools.get_dolar("oficial")

    assert result is not None
    assert result["tipo"] == "oficial"
    assert "compra" in result
    assert "venta" in result


@pytest.mark.asyncio
async def test_get_dolar_invalid_tipo():
    """Test que falla con tipo de dólar inválido."""
    with pytest.raises(Exception):
        # Esto debería fallar en la API o validación
        await tools.get_dolar("invalid_tipo")


@pytest.mark.asyncio
async def test_get_cotizaciones():
    """Test obtener todas las cotizaciones."""
    result = await tools.get_cotizaciones()

    assert result is not None
    assert isinstance(result, dict)
    assert len(result) > 0

    # Verificar que al menos blue y oficial estén presentes
    assert "blue" in result or "oficial" in result

    # Verificar estructura de una cotización
    for tipo, cotizacion in result.items():
        assert "compra" in cotizacion
        assert "venta" in cotizacion
        assert "fecha" in cotizacion


@pytest.mark.asyncio
async def test_convertir_usd_to_ars():
    """Test conversión de USD a ARS."""
    result = await tools.convertir(monto=100, de="USD", a="ARS", tipo_cambio="blue")

    assert result is not None
    assert result["monto_original"] == 100
    assert result["moneda_origen"] == "USD"
    assert result["moneda_destino"] == "ARS"
    assert result["tipo_cambio"] == "blue"
    assert result["cotizacion_usada"] == "venta"
    assert result["monto_convertido"] > 100  # ARS vale menos que USD


@pytest.mark.asyncio
async def test_convertir_ars_to_usd():
    """Test conversión de ARS a USD."""
    result = await tools.convertir(monto=100000, de="ARS", a="USD", tipo_cambio="blue")

    assert result is not None
    assert result["monto_original"] == 100000
    assert result["moneda_origen"] == "ARS"
    assert result["moneda_destino"] == "USD"
    assert result["tipo_cambio"] == "blue"
    assert result["cotizacion_usada"] == "compra"
    assert result["monto_convertido"] < 100000  # USD vale más que ARS


@pytest.mark.asyncio
async def test_convertir_same_currency():
    """Test que falla cuando origen y destino son iguales."""
    with pytest.raises(ValueError, match="La moneda origen y destino no pueden ser iguales"):
        await tools.convertir(monto=100, de="USD", a="USD", tipo_cambio="blue")


@pytest.mark.asyncio
async def test_convertir_negative_amount():
    """Test validación de monto negativo."""
    # Pydantic debería validar esto
    from pydantic import ValidationError

    with pytest.raises((ValidationError, ValueError)):
        _ = tools.ConvertirInput(monto=-100, de="USD", a="ARS", tipo_cambio="blue")
