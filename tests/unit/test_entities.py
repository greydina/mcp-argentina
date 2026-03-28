"""Tests de entidades del dominio."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from mcp_argentina.domain.entities.cotizacion import Cotizacion
from mcp_argentina.domain.entities.indicador import Indicador
from mcp_argentina.domain.entities.moneda import Moneda, TipoMoneda
from mcp_argentina.domain.value_objects.fecha import ARGENTINA_TZ, Fecha
from mcp_argentina.domain.value_objects.precio import Precio


class TestCotizacion:
    """Tests para entidad Cotizacion."""

    def test_crear_cotizacion_valida(self) -> None:
        """Debe crear una cotización válida."""
        fecha = Fecha.ahora()
        cotizacion = Cotizacion(
            nombre="Blue",
            compra=Precio(monto=Decimal("950"), moneda="ARS"),
            venta=Precio(monto=Decimal("970"), moneda="ARS"),
            fecha_actualizacion=fecha,
        )

        assert cotizacion.nombre == "Blue"
        assert cotizacion.compra.monto == Decimal("950")
        assert cotizacion.venta.monto == Decimal("970")

    def test_compra_mayor_que_venta_falla(self) -> None:
        """No debe permitir compra > venta."""
        fecha = Fecha.ahora()
        with pytest.raises(ValueError, match="no puede ser mayor"):
            Cotizacion(
                nombre="Blue",
                compra=Precio(monto=Decimal("1000"), moneda="ARS"),
                venta=Precio(monto=Decimal("900"), moneda="ARS"),
                fecha_actualizacion=fecha,
            )

    def test_spread_calcula_correctamente(self) -> None:
        """Debe calcular el spread correctamente."""
        fecha = Fecha.ahora()
        cotizacion = Cotizacion(
            nombre="Blue",
            compra=Precio(monto=Decimal("950"), moneda="ARS"),
            venta=Precio(monto=Decimal("970"), moneda="ARS"),
            fecha_actualizacion=fecha,
        )

        assert cotizacion.spread == Decimal("20")

    def test_promedio_calcula_correctamente(self) -> None:
        """Debe calcular el promedio correctamente."""
        fecha = Fecha.ahora()
        cotizacion = Cotizacion(
            nombre="Blue",
            compra=Precio(monto=Decimal("950"), moneda="ARS"),
            venta=Precio(monto=Decimal("970"), moneda="ARS"),
            fecha_actualizacion=fecha,
        )

        assert cotizacion.promedio == Decimal("960")

    def test_esta_actualizada_con_fecha_reciente(self) -> None:
        """Debe estar actualizada con fecha reciente."""
        fecha = Fecha.ahora()
        cotizacion = Cotizacion(
            nombre="Blue",
            compra=Precio(monto=Decimal("950"), moneda="ARS"),
            venta=Precio(monto=Decimal("970"), moneda="ARS"),
            fecha_actualizacion=fecha,
        )

        assert cotizacion.esta_actualizada(max_minutos=5) is True

    def test_esta_actualizada_con_fecha_antigua(self) -> None:
        """No debe estar actualizada con fecha antigua."""
        dt_antiguo = datetime.now(ARGENTINA_TZ) - timedelta(minutes=10)
        fecha = Fecha(dt_antiguo)
        cotizacion = Cotizacion(
            nombre="Blue",
            compra=Precio(monto=Decimal("950"), moneda="ARS"),
            venta=Precio(monto=Decimal("970"), moneda="ARS"),
            fecha_actualizacion=fecha,
        )

        assert cotizacion.esta_actualizada(max_minutos=5) is False

    def test_casa_default_es_dolarapi(self) -> None:
        """Casa por defecto debe ser dolarapi."""
        fecha = Fecha.ahora()
        cotizacion = Cotizacion(
            nombre="Blue",
            compra=Precio(monto=Decimal("950"), moneda="ARS"),
            venta=Precio(monto=Decimal("970"), moneda="ARS"),
            fecha_actualizacion=fecha,
        )

        assert cotizacion.casa == "dolarapi"


class TestIndicador:
    """Tests para entidad Indicador."""

    def test_crear_indicador_valido(self) -> None:
        """Debe crear un indicador válido."""
        fecha = Fecha.ahora()
        indicador = Indicador(
            nombre="Riesgo País",
            valor=Decimal("1850.5"),
            fecha=fecha,
            unidad="puntos básicos",
        )

        assert indicador.nombre == "Riesgo País"
        assert indicador.valor == Decimal("1850.5")
        assert indicador.unidad == "puntos básicos"

    def test_fuente_default_es_bcra(self) -> None:
        """Fuente por defecto debe ser BCRA."""
        fecha = Fecha.ahora()
        indicador = Indicador(
            nombre="Inflación",
            valor=Decimal("25.5"),
            fecha=fecha,
            unidad="%",
        )

        assert indicador.fuente == "BCRA"

    def test_str_formatea_correctamente(self) -> None:
        """Debe formatear el string correctamente."""
        fecha = Fecha.ahora()
        indicador = Indicador(
            nombre="Inflación",
            valor=Decimal("25.5"),
            fecha=fecha,
            unidad="%",
        )

        resultado = str(indicador)
        assert "Inflación" in resultado
        assert "25.5%" in resultado


class TestMoneda:
    """Tests para entidad Moneda."""

    def test_crear_moneda_valida(self) -> None:
        """Debe crear una moneda válida."""
        moneda = Moneda(codigo="ARS", nombre="Peso Argentino", simbolo="$")

        assert moneda.codigo == "ARS"
        assert moneda.nombre == "Peso Argentino"
        assert moneda.simbolo == "$"

    def test_moneda_no_soportada_falla(self) -> None:
        """No debe permitir monedas no soportadas."""
        with pytest.raises(ValueError, match="no soportada"):
            Moneda(codigo="EUR", nombre="Euro", simbolo="€")

    def test_peso_argentino_factory(self) -> None:
        """Factory de peso argentino."""
        moneda = Moneda.peso_argentino()

        assert moneda.codigo == "ARS"
        assert moneda.nombre == "Peso Argentino"
        assert moneda.simbolo == "$"

    def test_dolar_estadounidense_factory(self) -> None:
        """Factory de dólar estadounidense."""
        moneda = Moneda.dolar_estadounidense()

        assert moneda.codigo == "USD"
        assert moneda.nombre == "Dólar Estadounidense"
        assert moneda.simbolo == "US$"

    def test_tipo_moneda_enum_valores(self) -> None:
        """Enum debe tener los valores correctos."""
        assert TipoMoneda.ARS.value == "ARS"
        assert TipoMoneda.USD.value == "USD"
        assert len(TipoMoneda) == 2
