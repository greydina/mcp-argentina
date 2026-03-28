"""Tests de value objects."""

from datetime import datetime
from decimal import Decimal

import pytest

from mcp_argentina.domain.value_objects.fecha import ARGENTINA_TZ, Fecha
from mcp_argentina.domain.value_objects.precio import Precio


class TestPrecio:
    """Tests para Precio value object."""

    def test_crear_precio_valido(self) -> None:
        """Debe crear un precio válido."""
        precio = Precio(monto=Decimal("1000.50"), moneda="ARS")
        assert precio.monto == Decimal("1000.50")
        assert precio.moneda == "ARS"

    def test_precio_negativo_falla(self) -> None:
        """No debe permitir precios negativos."""
        with pytest.raises(ValueError, match="no puede ser negativo"):
            Precio(monto=Decimal("-100"), moneda="ARS")

    def test_moneda_invalida_falla(self) -> None:
        """No debe permitir monedas no soportadas."""
        with pytest.raises(ValueError, match="Moneda no soportada"):
            Precio(monto=Decimal("100"), moneda="EUR")

    def test_str_formatea_correctamente(self) -> None:
        """Debe formatear el string correctamente."""
        precio = Precio(monto=Decimal("1234.56"), moneda="ARS")
        assert str(precio) == "ARS 1234.56"

    def test_convertir_a_usd(self) -> None:
        """Debe convertir ARS a USD correctamente."""
        precio_ars = Precio(monto=Decimal("1000"), moneda="ARS")
        tasa = Decimal("950")
        precio_usd = precio_ars.convertir_a_usd(tasa)

        assert precio_usd.moneda == "USD"
        assert precio_usd.monto == Decimal("1000") / Decimal("950")

    def test_convertir_desde_usd_falla(self) -> None:
        """No debe convertir desde USD."""
        precio_usd = Precio(monto=Decimal("100"), moneda="USD")
        with pytest.raises(ValueError, match="Solo se puede convertir desde ARS"):
            precio_usd.convertir_a_usd(Decimal("950"))

    def test_convertir_con_tasa_negativa_falla(self) -> None:
        """No debe aceptar tasas negativas."""
        precio = Precio(monto=Decimal("1000"), moneda="ARS")
        with pytest.raises(ValueError, match="debe ser positiva"):
            precio.convertir_a_usd(Decimal("-950"))

    def test_precio_es_inmutable(self) -> None:
        """Precio debe ser inmutable (frozen dataclass)."""
        precio = Precio(monto=Decimal("1000"), moneda="ARS")
        with pytest.raises(AttributeError):
            precio.monto = Decimal("2000")  # type: ignore


class TestFecha:
    """Tests para Fecha value object."""

    def test_crear_fecha_con_timezone(self) -> None:
        """Debe crear fecha con timezone Argentina."""
        dt = datetime(2024, 3, 28, 15, 30, 0, tzinfo=ARGENTINA_TZ)
        fecha = Fecha(dt)
        assert fecha.valor.tzinfo == ARGENTINA_TZ

    def test_crear_fecha_sin_timezone_asume_argentina(self) -> None:
        """Debe asumir timezone Argentina si no se provee."""
        dt = datetime(2024, 3, 28, 15, 30, 0)
        fecha = Fecha(dt)
        assert fecha.valor.tzinfo == ARGENTINA_TZ

    def test_ahora_retorna_fecha_actual(self) -> None:
        """Debe retornar la fecha actual con timezone Argentina."""
        fecha = Fecha.ahora()
        assert fecha.valor.tzinfo == ARGENTINA_TZ
        # Verifica que es reciente (últimos 5 segundos)
        ahora = datetime.now(ARGENTINA_TZ)
        diferencia = (ahora - fecha.valor).total_seconds()
        assert 0 <= diferencia < 5

    def test_desde_iso_parsea_correctamente(self) -> None:
        """Debe parsear string ISO 8601."""
        iso_string = "2024-03-28T15:30:00-03:00"
        fecha = Fecha.desde_iso(iso_string)
        assert fecha.valor.year == 2024
        assert fecha.valor.month == 3
        assert fecha.valor.day == 28

    def test_es_hoy_con_fecha_actual(self) -> None:
        """Debe retornar True para fecha de hoy."""
        fecha = Fecha.ahora()
        assert fecha.es_hoy() is True

    def test_es_hoy_con_fecha_pasada(self) -> None:
        """Debe retornar False para fecha pasada."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=ARGENTINA_TZ)
        fecha = Fecha(dt)
        assert fecha.es_hoy() is False

    def test_str_formatea_correctamente(self) -> None:
        """Debe formatear el string correctamente."""
        dt = datetime(2024, 3, 28, 15, 30, 45, tzinfo=ARGENTINA_TZ)
        fecha = Fecha(dt)
        resultado = str(fecha)
        assert "2024-03-28" in resultado
        assert "15:30:45" in resultado

    def test_fecha_es_inmutable(self) -> None:
        """Fecha debe ser inmutable."""
        fecha = Fecha.ahora()
        with pytest.raises(AttributeError):
            fecha.valor = datetime.now()  # type: ignore
