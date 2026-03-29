"""Entidad Cotización."""

from dataclasses import dataclass
from decimal import Decimal

from mcp_argentina.domain.value_objects.fecha import Fecha
from mcp_argentina.domain.value_objects.precio import Precio


@dataclass
class Cotizacion:
    """Representa una cotización de dólar."""

    nombre: str  # "Blue", "Oficial", "MEP", etc.
    compra: Precio
    venta: Precio
    fecha_actualizacion: Fecha
    casa: str = "dolarapi"

    def __post_init__(self) -> None:
        """Validaciones."""
        if self.compra.valor > self.venta.valor:
            raise ValueError("El precio de compra no puede ser mayor que el de venta")

    @property
    def spread(self) -> Decimal:
        """Diferencia entre venta y compra."""
        return self.venta.valor - self.compra.valor

    @property
    def promedio(self) -> Decimal:
        """Precio promedio."""
        return (self.compra.valor + self.venta.valor) / 2

    def esta_actualizada(self, max_minutos: int = 5) -> bool:
        """Verifica si la cotización está actualizada."""
        ahora = Fecha.ahora()
        diferencia = (ahora.valor - self.fecha_actualizacion.valor).total_seconds()
        return diferencia <= (max_minutos * 60)
