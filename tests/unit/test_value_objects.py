"""Tests de value objects."""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from mcp_argentina.domain.value_objects.fecha import ARGENTINA_TZ, Fecha
from mcp_argentina.domain.value_objects.precio import Precio


class TestPrecio:
    """Tests para Precio value object."""

    def test_crear_precio_valido(self) -> None:
        """Debe crear un precio válido."""
        precio = Precio(valor=Decimal("1000.50"), moneda="ARS")
        assert precio.valor == Decimal("1000.50")
        assert precio.moneda == "ARS"

    def test_precio_negativo_falla(self) -> None:
        """No debe permitir precios negativos."""
        with pytest.raises(ValidationError, match="no puede ser negativo"):
            Precio(valor=Decimal("-100"), moneda="ARS")

    def test_moneda_minuscula_se_convierte(self) -> None:
        """Debe convertir moneda a mayúsculas."""
        precio = Precio(valor=Decimal("100"), moneda="ars")
        assert precio.moneda == "ARS"

    def test_str_formatea_correctamente(self) -> None:
        """Debe formatear el string correctamente."""
        precio = Precio(valor=Decimal("1234.56"), moneda="ARS")
        assert str(precio) == "1234.56 ARS"

    def test_suma_precios_misma_moneda(self) -> None:
        """Debe sumar precios de la misma moneda."""
        precio1 = Precio(valor=Decimal("100"), moneda="ARS")
        precio2 = Precio(valor=Decimal("200"), moneda="ARS")
        resultado = precio1 + precio2
        assert resultado.valor == Decimal("300")
        assert resultado.moneda == "ARS"

    def test_suma_precios_diferentes_monedas_falla(self) -> None:
        """No debe sumar precios de monedas diferentes."""
        precio_ars = Precio(valor=Decimal("100"), moneda="ARS")
        precio_usd = Precio(valor=Decimal("10"), moneda="USD")
        with pytest.raises(ValueError, match="monedas diferentes"):
            precio_ars + precio_usd

    def test_resta_precios(self) -> None:
        """Debe restar precios."""
        precio1 = Precio(valor=Decimal("200"), moneda="ARS")
        precio2 = Precio(valor=Decimal("100"), moneda="ARS")
        resultado = precio1 - precio2
        assert resultado.valor == Decimal("100")

    def test_multiplicacion_por_factor(self) -> None:
        """Debe multiplicar por un factor."""
        precio = Precio(valor=Decimal("100"), moneda="ARS")
        resultado = precio * 2
        assert resultado.valor == Decimal("200")

    def test_division_por_divisor(self) -> None:
        """Debe dividir por un divisor."""
        precio = Precio(valor=Decimal("100"), moneda="ARS")
        resultado = precio / 2
        assert resultado.valor == Decimal("50")

    def test_comparacion_precios(self) -> None:
        """Debe comparar precios correctamente."""
        precio1 = Precio(valor=Decimal("100"), moneda="ARS")
        precio2 = Precio(valor=Decimal("200"), moneda="ARS")
        assert precio1 < precio2
        assert precio2 > precio1

    def test_precio_es_inmutable(self) -> None:
        """Precio debe ser inmutable (frozen pydantic)."""
        precio = Precio(valor=Decimal("1000"), moneda="ARS")
        with pytest.raises(ValidationError):
            precio.valor = Decimal("2000")  # type: ignore


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
