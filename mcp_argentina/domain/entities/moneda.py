"""Entidad Moneda."""

from dataclasses import dataclass
from enum import Enum


class TipoMoneda(str, Enum):
    """Tipos de moneda soportados."""

    ARS = "ARS"
    USD = "USD"


@dataclass
class Moneda:
    """Representa una moneda."""

    codigo: str
    nombre: str
    simbolo: str

    def __post_init__(self) -> None:
        """Validaciones."""
        if self.codigo not in [t.value for t in TipoMoneda]:
            raise ValueError(f"Moneda no soportada: {self.codigo}")

    @classmethod
    def peso_argentino(cls) -> "Moneda":
        """Factory para ARS."""
        return cls(codigo="ARS", nombre="Peso Argentino", simbolo="$")

    @classmethod
    def dolar_estadounidense(cls) -> "Moneda":
        """Factory para USD."""
        return cls(codigo="USD", nombre="Dólar Estadounidense", simbolo="US$")
