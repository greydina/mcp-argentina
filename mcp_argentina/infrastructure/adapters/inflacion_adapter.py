"""
Adapter para datos de inflación desde argentinadatos.com.
"""

from dataclasses import dataclass
from datetime import date, datetime

import httpx


@dataclass(frozen=True)
class InflacionActual:
    """Datos de inflación actual."""

    mensual: float  # Último mes disponible
    interanual: float  # Últimos 12 meses acumulado
    acumulada_anio: float  # Acumulada en el año
    fecha_ultimo_dato: date


@dataclass(frozen=True)
class InflacionMes:
    """Inflación de un mes específico."""

    fecha: date
    valor: float


class InflacionAdapter:
    """
    Adapter para datos de inflación de Argentina.

    Fuente: INDEC vía argentinadatos.com

    Example:
        >>> adapter = InflacionAdapter()
        >>> inflacion = await adapter.obtener_actual()
        >>> print(f"Mensual: {inflacion.mensual}%")
        >>> print(f"Interanual: {inflacion.interanual}%")
    """

    BASE_URL = "https://api.argentinadatos.com/v1"

    def __init__(self, client: httpx.AsyncClient | None = None):
        """Inicializa el adapter."""
        self._client = client
        self._owns_client = client is None

    def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea el cliente HTTP."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self._client

    async def obtener_historico(self, meses: int = 24) -> list[InflacionMes]:
        """
        Obtiene histórico de inflación mensual.

        Args:
            meses: Cantidad de meses hacia atrás

        Returns:
            Lista de inflación mensual ordenada por fecha
        """
        url = f"{self.BASE_URL}/finanzas/indices/inflacion"

        client = self._get_client()
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        inflaciones = []
        for item in data:
            fecha_str = item.get("fecha", "")
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            inflaciones.append(
                InflacionMes(
                    fecha=fecha,
                    valor=float(item.get("valor", 0)),
                )
            )

        inflaciones.sort(key=lambda x: x.fecha)
        return inflaciones[-meses:]

    async def obtener_actual(self) -> InflacionActual:
        """
        Obtiene inflación actual con cálculos.

        Returns:
            InflacionActual con mensual, interanual y acumulada
        """
        historico = await self.obtener_historico(meses=13)

        if not historico:
            return InflacionActual(
                mensual=0,
                interanual=0,
                acumulada_anio=0,
                fecha_ultimo_dato=date.today(),
            )

        # Último mes
        ultimo = historico[-1]
        mensual = ultimo.valor

        # Interanual (últimos 12 meses, compuesto)
        ultimos_12 = historico[-12:] if len(historico) >= 12 else historico
        interanual = self._calcular_acumulada(ultimos_12)

        # Acumulada en el año (desde enero)
        anio_actual = ultimo.fecha.year
        meses_anio = [m for m in historico if m.fecha.year == anio_actual]
        acumulada = self._calcular_acumulada(meses_anio)

        return InflacionActual(
            mensual=round(mensual, 2),
            interanual=round(interanual, 2),
            acumulada_anio=round(acumulada, 2),
            fecha_ultimo_dato=ultimo.fecha,
        )

    def _calcular_acumulada(self, meses: list[InflacionMes]) -> float:
        """Calcula inflación acumulada (compuesta)."""
        if not meses:
            return 0

        acumulada = 1.0
        for mes in meses:
            acumulada *= 1 + (mes.valor / 100)

        return (acumulada - 1) * 100

    async def obtener_por_anio(self, anio: int) -> float | None:
        """
        Obtiene inflación anual de un año específico.

        Args:
            anio: Año (ej: 2024, 2025)

        Returns:
            Inflación anual acumulada o None si no hay datos
        """
        historico = await self.obtener_historico(meses=120)  # ~10 años
        meses_anio = [m for m in historico if m.fecha.year == anio]

        if not meses_anio:
            return None

        return round(self._calcular_acumulada(meses_anio), 2)

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._owns_client and self._client:
            await self._client.aclose()
            self._client = None
