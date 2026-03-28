"""MCP Server principal."""

from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter


class MCPArgentinaServer:
    """Servidor MCP para datos económicos de Argentina."""

    def __init__(self) -> None:
        """Inicializa el servidor."""
        self.dolarapi = DolarAPIAdapter()

    async def get_dolar(self, tipo: str) -> dict:
        """Tool: get_dolar - Obtiene cotización de dólar.

        Args:
            tipo: Tipo de dólar (oficial, blue, mep, ccl, tarjeta, cripto)

        Returns:
            Dict con datos de la cotización
        """
        cotizacion = await self.dolarapi.obtener_dolar(tipo)

        return {
            "tipo": cotizacion.nombre,
            "compra": float(cotizacion.compra.monto),
            "venta": float(cotizacion.venta.monto),
            "promedio": float(cotizacion.promedio),
            "spread": float(cotizacion.spread),
            "fecha_actualizacion": str(cotizacion.fecha_actualizacion),
            "casa": cotizacion.casa,
        }

    async def get_cotizaciones(self) -> dict:
        """Tool: get_cotizaciones - Obtiene todas las cotizaciones.

        Returns:
            Dict con todas las cotizaciones disponibles
        """
        cotizaciones = await self.dolarapi.obtener_todas()

        return {
            "cotizaciones": [
                {
                    "tipo": cot.nombre,
                    "compra": float(cot.compra.monto),
                    "venta": float(cot.venta.monto),
                    "promedio": float(cot.promedio),
                }
                for cot in cotizaciones
            ],
            "total": len(cotizaciones),
        }

    async def close(self) -> None:
        """Cierra recursos."""
        await self.dolarapi.close()
