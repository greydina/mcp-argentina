"""Value Object Precio - Representa un valor monetario."""

from decimal import Decimal
from typing_extensions import Self

from pydantic import BaseModel, Field, field_validator


class Precio(BaseModel):
    """
    Value object que representa un precio o valor monetario.

    Un precio siempre está asociado a una moneda específica y usa
    Decimal para garantizar precisión en cálculos financieros.

    Attributes:
        valor: Cantidad numérica del precio (Decimal para precisión)
        moneda: Código ISO 4217 de la moneda (ej: "ARS", "USD")

    Example:
        >>> precio_ars = Precio(valor=Decimal("1250.50"), moneda="ARS")
        >>> precio_usd = Precio(valor=Decimal("100.00"), moneda="USD")
        >>> precio_ars > precio_usd  # ValueError: monedas diferentes
    """

    model_config = {"frozen": True}

    valor: Decimal = Field(
        ...,
        description="Valor numérico del precio (usa Decimal para precisión)",
    )
    moneda: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Código ISO 4217 de moneda (ej: ARS, USD, EUR)",
    )

    @field_validator("moneda")
    @classmethod
    def validar_moneda_uppercase(cls, v: str) -> str:
        """Valida que el código de moneda esté en mayúsculas."""
        return v.upper()

    @field_validator("valor")
    @classmethod
    def validar_valor_no_negativo(cls, v: Decimal) -> Decimal:
        """Valida que el valor no sea negativo."""
        if v < 0:
            raise ValueError("El valor del precio no puede ser negativo")
        return v

    def __add__(self, other: Self) -> Self:
        """
        Suma dos precios.

        Args:
            other: Otro precio a sumar

        Returns:
            Nuevo precio con la suma

        Raises:
            ValueError: Si las monedas no coinciden
        """
        if not isinstance(other, Precio):
            raise TypeError(f"No se puede sumar Precio con {type(other)}")
        if self.moneda != other.moneda:
            raise ValueError(
                f"No se pueden sumar precios con monedas diferentes: "
                f"{self.moneda} vs {other.moneda}"
            )
        return Precio(valor=self.valor + other.valor, moneda=self.moneda)

    def __sub__(self, other: Self) -> Self:
        """
        Resta dos precios.

        Args:
            other: Precio a restar

        Returns:
            Nuevo precio con la resta (puede ser negativo)

        Raises:
            ValueError: Si las monedas no coinciden
        """
        if not isinstance(other, Precio):
            raise TypeError(f"No se puede restar Precio con {type(other)}")
        if self.moneda != other.moneda:
            raise ValueError(
                f"No se pueden restar precios con monedas diferentes: "
                f"{self.moneda} vs {other.moneda}"
            )
        # Permitimos valores negativos en resta (para representar pérdidas/spreads)
        return Precio.model_construct(valor=self.valor - other.valor, moneda=self.moneda)

    def __mul__(self, factor: float | Decimal) -> Self:
        """
        Multiplica el precio por un factor.

        Args:
            factor: Factor de multiplicación

        Returns:
            Nuevo precio multiplicado

        Example:
            >>> precio = Precio(valor=Decimal("100"), moneda="USD")
            >>> precio * 1.5  # Precio(valor=Decimal("150"), moneda="USD")
        """
        if not isinstance(factor, (int, float, Decimal)):
            raise TypeError(f"No se puede multiplicar Precio por {type(factor)}")
        return Precio(valor=self.valor * Decimal(str(factor)), moneda=self.moneda)

    def __truediv__(self, divisor: float | Decimal) -> Self:
        """
        Divide el precio por un divisor.

        Args:
            divisor: Divisor

        Returns:
            Nuevo precio dividido

        Raises:
            ZeroDivisionError: Si el divisor es cero
        """
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError(f"No se puede dividir Precio por {type(divisor)}")
        if divisor == 0:
            raise ZeroDivisionError("No se puede dividir un precio por cero")
        return Precio(valor=self.valor / Decimal(str(divisor)), moneda=self.moneda)

    def __lt__(self, other: Self) -> bool:
        """Operador menor que (<)."""
        if not isinstance(other, Precio):
            raise TypeError(f"No se puede comparar Precio con {type(other)}")
        if self.moneda != other.moneda:
            raise ValueError(
                f"No se pueden comparar precios con monedas diferentes: "
                f"{self.moneda} vs {other.moneda}"
            )
        return self.valor < other.valor

    def __le__(self, other: Self) -> bool:
        """Operador menor o igual que (<=)."""
        return self == other or self < other

    def __gt__(self, other: Self) -> bool:
        """Operador mayor que (>)."""
        if not isinstance(other, Precio):
            raise TypeError(f"No se puede comparar Precio con {type(other)}")
        if self.moneda != other.moneda:
            raise ValueError(
                f"No se pueden comparar precios con monedas diferentes: "
                f"{self.moneda} vs {other.moneda}"
            )
        return self.valor > other.valor

    def __ge__(self, other: Self) -> bool:
        """Operador mayor o igual que (>=)."""
        return self == other or self > other

    def __str__(self) -> str:
        """Representación en string legible."""
        return f"{self.valor:.2f} {self.moneda}"

    def __repr__(self) -> str:
        """Representación técnica."""
        return f"Precio(valor=Decimal('{self.valor}'), moneda='{self.moneda}')"
