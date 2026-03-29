"""Fixtures compartidas para todos los tests."""

from datetime import datetime
from decimal import Decimal

import httpx
import pytest
from pytest_httpx import HTTPXMock

from mcp_argentina.domain.entities.cotizacion import Cotizacion
from mcp_argentina.domain.entities.indicador import Indicador
from mcp_argentina.domain.entities.moneda import Moneda
from mcp_argentina.domain.value_objects.fecha import ARGENTINA_TZ, Fecha
from mcp_argentina.domain.value_objects.precio import Precio
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter


@pytest.fixture
def precio_ars() -> Precio:
    """Fixture de precio en ARS."""
    return Precio(valor=Decimal("1000.50"), moneda="ARS")


@pytest.fixture
def precio_usd() -> Precio:
    """Fixture de precio en USD."""
    return Precio(valor=Decimal("10.25"), moneda="USD")


@pytest.fixture
def fecha_actual() -> Fecha:
    """Fixture de fecha actual."""
    return Fecha.ahora()


@pytest.fixture
def fecha_pasada() -> Fecha:
    """Fixture de fecha pasada."""
    dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=ARGENTINA_TZ)
    return Fecha(dt)


@pytest.fixture
def cotizacion_blue(fecha_actual: Fecha) -> Cotizacion:
    """Fixture de cotización dólar blue."""
    return Cotizacion(
        nombre="Blue",
        compra=Precio(valor=Decimal("950.00"), moneda="ARS"),
        venta=Precio(valor=Decimal("970.00"), moneda="ARS"),
        fecha_actualizacion=fecha_actual,
        casa="dolarapi",
    )


@pytest.fixture
def cotizacion_oficial(fecha_actual: Fecha) -> Cotizacion:
    """Fixture de cotización dólar oficial."""
    return Cotizacion(
        nombre="Oficial",
        compra=Precio(valor=Decimal("800.00"), moneda="ARS"),
        venta=Precio(valor=Decimal("810.00"), moneda="ARS"),
        fecha_actualizacion=fecha_actual,
        casa="dolarapi",
    )


@pytest.fixture
def indicador_riesgo_pais(fecha_actual: Fecha) -> Indicador:
    """Fixture de indicador riesgo país."""
    return Indicador(
        nombre="Riesgo País",
        valor=Decimal("1850.5"),
        fecha=fecha_actual,
        unidad="puntos básicos",
        fuente="dolarapi",
    )


@pytest.fixture
def moneda_ars() -> Moneda:
    """Fixture de moneda ARS."""
    return Moneda.peso_argentino()


@pytest.fixture
def moneda_usd() -> Moneda:
    """Fixture de moneda USD."""
    return Moneda.dolar_estadounidense()


@pytest.fixture
def mock_dolarapi_blue_response() -> dict:
    """Mock de respuesta de dolarapi para dólar blue."""
    return {
        "compra": 950.0,
        "venta": 970.0,
        "fechaActualizacion": "2024-03-28T15:30:00-03:00",
    }


@pytest.fixture
def mock_dolarapi_oficial_response() -> dict:
    """Mock de respuesta de dolarapi para dólar oficial."""
    return {
        "compra": 800.0,
        "venta": 810.0,
        "fechaActualizacion": "2024-03-28T15:30:00-03:00",
    }


@pytest.fixture
async def http_client() -> httpx.AsyncClient:
    """Cliente HTTP para tests."""
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
def httpx_mock(httpx_mock: HTTPXMock) -> HTTPXMock:
    """Mock de httpx (provisto por pytest-httpx)."""
    return httpx_mock


@pytest.fixture
async def dolarapi_adapter() -> DolarAPIAdapter:
    """Adapter de dolarapi con cliente mock."""
    adapter = DolarAPIAdapter()
    yield adapter
    await adapter.close()
