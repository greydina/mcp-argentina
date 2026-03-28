"""Entidad Indicador Económico."""

from dataclasses import dataclass
from decimal import Decimal

from mcp_argentina.domain.value_objects.fecha import Fecha


@dataclass
class Indicador:
    """Representa un indicador económico."""

    nombre: str  # "Inflación", "Riesgo País", etc.
    valor: Decimal
    fecha: Fecha
    unidad: str  # "%", "puntos básicos", etc.
    fuente: str = "BCRA"

    def __str__(self) -> str:
        return f"{self.nombre}: {self.valor}{self.unidad} ({self.fecha})"
