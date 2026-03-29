"""
Adapter para datos históricos desde argentinadatos.com.

Provee acceso a:
- Históricos de cotizaciones del dólar
- Históricos de inflación
- Históricos de riesgo país
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

import httpx


@dataclass(frozen=True)
class CotizacionHistorica:
    """Cotización histórica de un día específico."""

    fecha: date
    casa: str
    compra: Decimal
    venta: Decimal

    @property
    def promedio(self) -> Decimal:
        """Precio promedio."""
        return (self.compra + self.venta) / 2


@dataclass(frozen=True)
class InflacionMensual:
    """Inflación de un mes específico."""

    fecha: date  # Primer día del mes
    valor: float  # Porcentaje


@dataclass(frozen=True)
class RiesgoPaisHistorico:
    """Riesgo país de un día específico."""

    fecha: date
    valor: int


class HistoricosAdapter:
    """
    Adapter para datos históricos de Argentina.

    Usa la API de argentinadatos.com que provee datos desde 2011.

    Example:
        >>> adapter = HistoricosAdapter()
        >>> historicos = await adapter.obtener_historico_dolar("blue", dias=30)
        >>> for h in historicos[-5:]:
        ...     print(f"{h.fecha}: ${h.venta}")
    """

    BASE_URL = "https://api.argentinadatos.com/v1"

    CASAS_MAP = {
        "blue": "blue",
        "oficial": "oficial",
        "mep": "bolsa",
        "ccl": "contadoconliqui",
        "tarjeta": "tarjeta",
        "mayorista": "mayorista",
        "cripto": "cripto",
    }

    def __init__(self, client: httpx.AsyncClient | None = None):
        """Inicializa el adapter."""
        self._client = client
        self._owns_client = client is None

    def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea el cliente HTTP."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self._client

    async def obtener_historico_dolar(
        self,
        tipo: str = "blue",
        dias: int = 30,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> list[CotizacionHistorica]:
        """
        Obtiene histórico de cotizaciones del dólar.

        Args:
            tipo: Tipo de dólar (blue, oficial, mep, ccl, etc.)
            dias: Cantidad de días hacia atrás (si no se especifica desde/hasta)
            desde: Fecha inicio (opcional)
            hasta: Fecha fin (opcional, default: hoy)

        Returns:
            Lista de cotizaciones ordenadas por fecha ascendente
        """
        tipo_lower = tipo.lower()
        if tipo_lower not in self.CASAS_MAP:
            raise ValueError(f"Tipo '{tipo}' no válido")

        casa = self.CASAS_MAP[tipo_lower]
        url = f"{self.BASE_URL}/cotizaciones/dolares/{casa}"

        client = self._get_client()
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        # Filtrar por fechas
        if hasta is None:
            hasta = date.today()
        if desde is None:
            desde = hasta - timedelta(days=dias)

        cotizaciones = []
        for item in data:
            fecha_str = item.get("fecha", "")
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            if desde <= fecha <= hasta:
                cotizaciones.append(
                    CotizacionHistorica(
                        fecha=fecha,
                        casa=tipo_lower,
                        compra=Decimal(str(item.get("compra", 0))),
                        venta=Decimal(str(item.get("venta", 0))),
                    )
                )

        return sorted(cotizaciones, key=lambda x: x.fecha)

    async def obtener_historico_inflacion(
        self,
        meses: int = 12,
    ) -> list[InflacionMensual]:
        """
        Obtiene histórico de inflación mensual.

        Args:
            meses: Cantidad de meses hacia atrás

        Returns:
            Lista de inflación mensual ordenada por fecha ascendente
        """
        url = f"{self.BASE_URL}/finanzas/indices/inflacion"

        client = self._get_client()
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        # Tomar los últimos N meses
        inflaciones = []
        for item in data:
            fecha_str = item.get("fecha", "")
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            inflaciones.append(
                InflacionMensual(
                    fecha=fecha,
                    valor=float(item.get("valor", 0)),
                )
            )

        # Ordenar y tomar últimos N
        inflaciones.sort(key=lambda x: x.fecha)
        return inflaciones[-meses:]

    async def obtener_historico_riesgo_pais(
        self,
        dias: int = 30,
    ) -> list[RiesgoPaisHistorico]:
        """
        Obtiene histórico de riesgo país.

        Args:
            dias: Cantidad de días hacia atrás

        Returns:
            Lista de riesgo país ordenada por fecha ascendente
        """
        url = f"{self.BASE_URL}/finanzas/indices/riesgo-pais"

        client = self._get_client()
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        fecha_limite = date.today() - timedelta(days=dias)

        historicos = []
        for item in data:
            fecha_str = item.get("fecha", "")
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            if fecha >= fecha_limite:
                historicos.append(
                    RiesgoPaisHistorico(
                        fecha=fecha,
                        valor=int(item.get("valor", 0)),
                    )
                )

        return sorted(historicos, key=lambda x: x.fecha)

    async def obtener_variacion_dolar(
        self,
        tipo: str = "blue",
        dias: int = 7,
    ) -> dict[str, str | float]:
        """
        Calcula la variación porcentual del dólar.

        Args:
            tipo: Tipo de dólar
            dias: Período de comparación

        Returns:
            Dict con variación absoluta y porcentual
        """
        historicos = await self.obtener_historico_dolar(tipo, dias=dias + 1)

        if len(historicos) < 2:
            return {"variacion_absoluta": 0, "variacion_porcentual": 0}

        inicio = historicos[0].venta
        fin = historicos[-1].venta

        variacion_abs = fin - inicio
        variacion_pct = float((variacion_abs / inicio) * 100) if inicio > 0 else 0

        return {
            "fecha_inicio": historicos[0].fecha.isoformat(),
            "fecha_fin": historicos[-1].fecha.isoformat(),
            "valor_inicio": float(inicio),
            "valor_fin": float(fin),
            "variacion_absoluta": float(variacion_abs),
            "variacion_porcentual": round(variacion_pct, 2),
        }

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._owns_client and self._client:
            await self._client.aclose()
            self._client = None
