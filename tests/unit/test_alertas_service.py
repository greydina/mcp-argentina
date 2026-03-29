"""Tests para AlertasService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

from mcp_argentina.application.services.alertas_service import (
    AlertasService,
    ConfiguracionAlerta,
    TipoAlerta,
)
from mcp_argentina.domain.entities.cotizacion import Cotizacion
from mcp_argentina.domain.value_objects.precio import Precio
from mcp_argentina.domain.value_objects.fecha import Fecha


@pytest.fixture
def mock_repository():
    """Mock del repositorio."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def cotizacion_blue():
    """Cotización blue de ejemplo."""
    return Cotizacion(
        nombre="Blue",
        compra=Precio(valor=Decimal("1350"), moneda="ARS"),
        venta=Precio(valor=Decimal("1400"), moneda="ARS"),
        fecha_actualizacion=Fecha.ahora(),
        casa="dolarapi",
    )


class TestAlertasService:
    """Tests del servicio de alertas."""

    def test_configurar_alerta(self, mock_repository) -> None:
        """Debe configurar una alerta."""
        service = AlertasService(mock_repository)
        
        config = ConfiguracionAlerta(
            cotizacion="blue",
            umbral_porcentual=5.0,
        )
        service.configurar_alerta(config)
        
        configs = service.obtener_configuraciones()
        assert len(configs) == 1
        assert configs[0].cotizacion == "blue"

    def test_configurar_alerta_reemplaza_existente(self, mock_repository) -> None:
        """Debe reemplazar configuración existente para misma cotización."""
        service = AlertasService(mock_repository)
        
        service.configurar_alerta(ConfiguracionAlerta(
            cotizacion="blue", umbral_porcentual=5.0
        ))
        service.configurar_alerta(ConfiguracionAlerta(
            cotizacion="blue", umbral_porcentual=10.0
        ))
        
        configs = service.obtener_configuraciones()
        assert len(configs) == 1
        assert configs[0].umbral_porcentual == 10.0

    @pytest.mark.asyncio
    async def test_verificar_alerta_sin_cambio(
        self, mock_repository, cotizacion_blue
    ) -> None:
        """No debe generar alerta si no hay cambio significativo."""
        mock_repository.obtener_dolar.return_value = cotizacion_blue
        service = AlertasService(mock_repository)
        
        service.configurar_alerta(ConfiguracionAlerta(
            cotizacion="blue", umbral_porcentual=5.0
        ))
        
        # Primera verificación establece referencia
        alertas1 = await service.verificar_alertas()
        # Segunda verificación sin cambio
        alertas2 = await service.verificar_alertas()
        
        assert len(alertas2) == 0

    @pytest.mark.asyncio
    async def test_verificar_alerta_umbral_superado(
        self, mock_repository
    ) -> None:
        """Debe generar alerta si se supera valor máximo."""
        cot_alta = Cotizacion(
            nombre="Blue",
            compra=Precio(valor=Decimal("1550"), moneda="ARS"),
            venta=Precio(valor=Decimal("1600"), moneda="ARS"),
            fecha_actualizacion=Fecha.ahora(),
            casa="dolarapi",
        )
        mock_repository.obtener_dolar.return_value = cot_alta
        
        service = AlertasService(mock_repository)
        service.configurar_alerta(ConfiguracionAlerta(
            cotizacion="blue", valor_maximo=1500.0
        ))
        
        alertas = await service.verificar_alertas()
        
        assert len(alertas) == 1
        assert alertas[0].tipo == TipoAlerta.UMBRAL_SUPERADO

    @pytest.mark.asyncio
    async def test_callback_se_llama(
        self, mock_repository
    ) -> None:
        """Debe llamar callbacks cuando se genera alerta."""
        cot_alta = Cotizacion(
            nombre="Blue",
            compra=Precio(valor=Decimal("1550"), moneda="ARS"),
            venta=Precio(valor=Decimal("1600"), moneda="ARS"),
            fecha_actualizacion=Fecha.ahora(),
            casa="dolarapi",
        )
        mock_repository.obtener_dolar.return_value = cot_alta
        
        callback = AsyncMock()
        service = AlertasService(mock_repository)
        service.registrar_callback(callback)
        service.configurar_alerta(ConfiguracionAlerta(
            cotizacion="blue", valor_maximo=1500.0
        ))
        
        await service.verificar_alertas()
        
        callback.assert_called_once()
