"""Tests para GraficosService."""

from datetime import date, timedelta

from mcp_argentina.application.services.graficos_service import (
    GraficosService,
    PuntoGrafico,
)


class TestGraficosService:
    """Tests del servicio de gráficos."""

    def test_generar_linea_basico(self) -> None:
        """Debe generar gráfico de línea básico."""
        service = GraficosService()
        hoy = date.today()

        datos = [
            PuntoGrafico(fecha=hoy - timedelta(days=2), valor=1400),
            PuntoGrafico(fecha=hoy - timedelta(days=1), valor=1420),
            PuntoGrafico(fecha=hoy, valor=1450),
        ]

        grafico = service.generar_linea(datos, titulo="Test")

        assert "Test" in grafico
        assert "▁" in grafico or "▂" in grafico or "█" in grafico

    def test_generar_linea_sin_datos(self) -> None:
        """Debe manejar lista vacía."""
        service = GraficosService()
        grafico = service.generar_linea([])

        assert "Sin datos" in grafico

    def test_generar_linea_muestra_variacion(self) -> None:
        """Debe mostrar variación porcentual."""
        service = GraficosService()
        hoy = date.today()

        datos = [
            PuntoGrafico(fecha=hoy - timedelta(days=1), valor=1000),
            PuntoGrafico(fecha=hoy, valor=1100),  # +10%
        ]

        grafico = service.generar_linea(datos)

        assert "📈" in grafico
        assert "10" in grafico

    def test_generar_barras(self) -> None:
        """Debe generar gráfico de barras."""
        service = GraficosService()

        datos = [
            ("Blue", 1400),
            ("Oficial", 950),
            ("MEP", 1320),
        ]

        grafico = service.generar_barras(datos, titulo="Cotizaciones")

        assert "Cotizaciones" in grafico
        assert "Blue" in grafico
        assert "█" in grafico

    def test_generar_comparacion(self) -> None:
        """Debe generar comparación entre valores."""
        service = GraficosService()

        comparacion = service.generar_comparacion(
            valor1=1000,
            valor2=1100,
            etiqueta1="Ayer",
            etiqueta2="Hoy",
        )

        assert "Ayer" in comparacion
        assert "Hoy" in comparacion
        assert "📈" in comparacion
        assert "10" in comparacion  # 10% variación

    def test_generar_comparacion_bajada(self) -> None:
        """Debe mostrar bajada con emoji correcto."""
        service = GraficosService()

        comparacion = service.generar_comparacion(
            valor1=1100,
            valor2=1000,
        )

        assert "📉" in comparacion

    def test_generar_tabla(self) -> None:
        """Debe generar tabla ASCII."""
        service = GraficosService()

        datos = [
            {"tipo": "Blue", "valor": 1400},
            {"tipo": "Oficial", "valor": 950},
        ]

        tabla = service.generar_tabla(datos, columnas=["tipo", "valor"])

        assert "Blue" in tabla
        assert "Oficial" in tabla
        assert "1400" in tabla

    def test_generar_tabla_vacia(self) -> None:
        """Debe manejar datos vacíos."""
        service = GraficosService()
        tabla = service.generar_tabla([], columnas=[])

        assert "Sin datos" in tabla
