"""Tests de integración contra dolarapi.com real.

IMPORTANTE: Estos tests hacen requests reales a la API.
- Marcados como @pytest.mark.slow
- Ejecutar con: pytest -m slow
- Pueden fallar si la API está caída o hay problemas de red
"""

import pytest

from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter


@pytest.mark.slow
@pytest.mark.integration
class TestDolarAPIIntegration:
    """Tests de integración contra la API real."""

    @pytest.mark.asyncio
    async def test_obtener_dolar_blue_real(self) -> None:
        """Debe obtener dólar blue desde la API real."""
        adapter = DolarAPIAdapter()

        try:
            cotizacion = await adapter.obtener_dolar("blue")

            # Validaciones básicas
            assert cotizacion.nombre == "Blue"
            assert cotizacion.compra.monto > 0
            assert cotizacion.venta.monto > 0
            assert cotizacion.venta.monto > cotizacion.compra.monto
            assert cotizacion.casa == "dolarapi"
            assert cotizacion.esta_actualizada(max_minutos=60)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_dolar_oficial_real(self) -> None:
        """Debe obtener dólar oficial desde la API real."""
        adapter = DolarAPIAdapter()

        try:
            cotizacion = await adapter.obtener_dolar("oficial")

            assert cotizacion.nombre == "Oficial"
            assert cotizacion.compra.monto > 0
            assert cotizacion.venta.monto > 0
            # El oficial suele tener spread más bajo que el blue
            assert cotizacion.spread < 50

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    async def test_obtener_todas_real(self) -> None:
        """Debe obtener todas las cotizaciones desde la API real."""
        adapter = DolarAPIAdapter()

        try:
            cotizaciones = await adapter.obtener_todas()

            # Debe retornar al menos algunas cotizaciones
            assert len(cotizaciones) > 0

            # Verificar que todas tienen datos válidos
            for cot in cotizaciones:
                assert cot.compra.monto > 0
                assert cot.venta.monto > 0
                assert cot.venta.monto >= cot.compra.monto
                assert cot.esta_actualizada(max_minutos=60)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    async def test_todos_los_tipos_disponibles(self) -> None:
        """Debe poder obtener todos los tipos de dólar."""
        adapter = DolarAPIAdapter()
        tipos = ["oficial", "blue", "mep", "ccl", "tarjeta", "cripto"]

        try:
            for tipo in tipos:
                cotizacion = await adapter.obtener_dolar(tipo)
                assert cotizacion.compra.monto > 0
                assert cotizacion.venta.monto > 0

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    async def test_comparar_oficial_vs_blue(self) -> None:
        """El blue debería ser mayor que el oficial."""
        adapter = DolarAPIAdapter()

        try:
            oficial = await adapter.obtener_dolar("oficial")
            blue = await adapter.obtener_dolar("blue")

            # El blue normalmente es más caro
            assert blue.promedio > oficial.promedio

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    async def test_formato_fecha_actualizacion(self) -> None:
        """La fecha de actualización debe tener formato correcto."""
        adapter = DolarAPIAdapter()

        try:
            cotizacion = await adapter.obtener_dolar("blue")

            # Verificar que la fecha tiene timezone
            assert cotizacion.fecha_actualizacion.valor.tzinfo is not None
            # Debe ser una fecha reciente (menos de 24 horas)
            assert cotizacion.esta_actualizada(max_minutos=1440)

        finally:
            await adapter.close()
