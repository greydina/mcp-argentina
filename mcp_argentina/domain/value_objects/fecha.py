"""Value object para fechas con timezone Argentina."""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

ARGENTINA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")


@dataclass(frozen=True)
class Fecha:
    """Fecha con timezone Argentina."""

    valor: datetime

    def __post_init__(self) -> None:
        """Asegura que tenga timezone."""
        if self.valor.tzinfo is None:
            # Si no tiene TZ, asume Argentina
            object.__setattr__(self, "valor", self.valor.replace(tzinfo=ARGENTINA_TZ))

    @classmethod
    def ahora(cls) -> "Fecha":
        """Retorna la fecha actual en timezone Argentina."""
        return cls(datetime.now(ARGENTINA_TZ))

    @classmethod
    def desde_iso(cls, iso_string: str) -> "Fecha":
        """Parse desde ISO 8601."""
        # Reemplazar Z por +00:00 para compatibilidad con Python 3.10
        if iso_string.endswith("Z"):
            iso_string = iso_string[:-1] + "+00:00"
        dt = datetime.fromisoformat(iso_string)
        return cls(dt)

    def es_hoy(self) -> bool:
        """Verifica si la fecha es hoy."""
        hoy = self.ahora()
        return (
            self.valor.year == hoy.valor.year
            and self.valor.month == hoy.valor.month
            and self.valor.day == hoy.valor.day
        )

    def __str__(self) -> str:
        return self.valor.strftime("%Y-%m-%d %H:%M:%S %Z")
