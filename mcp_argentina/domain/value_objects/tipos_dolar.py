"""Value Object TipoDolar - Enum de tipos de dólar en Argentina."""

from enum import Enum


class TipoDolar(str, Enum):
    """
    Tipos de cotización del dólar en Argentina.

    Este enum estandariza los diferentes tipos de cambio del dólar
    que existen en el mercado argentino, cada uno con características
    y regulaciones específicas.

    Attributes:
        OFICIAL: Dólar oficial del BCRA (controlado, para importaciones)
        BLUE: Dólar paralelo/informal (mercado negro)
        MEP: Dólar MEP (Mercado Electrónico de Pagos, vía bonos AL30)
        CCL: Dólar CCL (Contado con Liquidación, vía bonos GD30)
        CRIPTO: Dólar cripto (precio implícito en exchanges de criptomonedas)
        TARJETA: Dólar tarjeta (oficial + impuestos PAIS y ganancias)
        MAYORISTA: Dólar mayorista (interbancario, grandes volúmenes)
        SOLIDARIO: Dólar solidario (oficial + impuesto PAIS, para consumo)
        BOLSA: Dólar bolsa (similar a MEP, vía diferentes bonos)
        TURISTA: Dólar turista (para gastos en el exterior)

    Example:
        >>> tipo = TipoDolar.BLUE
        >>> tipo.value  # "blue"
        >>> tipo.descripcion()  # "Dólar paralelo/informal (mercado negro)"
        >>> TipoDolar("blue")  # TipoDolar.BLUE
    """

    OFICIAL = "oficial"
    BLUE = "blue"
    MEP = "mep"
    CCL = "ccl"
    CRIPTO = "cripto"
    TARJETA = "tarjeta"
    MAYORISTA = "mayorista"
    SOLIDARIO = "solidario"
    BOLSA = "bolsa"
    TURISTA = "turista"

    def descripcion(self) -> str:
        """
        Retorna una descripción legible del tipo de dólar.

        Returns:
            Descripción en español del tipo de cambio
        """
        descripciones = {
            self.OFICIAL: "Dólar oficial del BCRA (controlado, para importaciones)",
            self.BLUE: "Dólar paralelo/informal (mercado negro)",
            self.MEP: "Dólar MEP (Mercado Electrónico de Pagos, vía bonos AL30)",
            self.CCL: "Dólar CCL (Contado con Liquidación, vía bonos GD30)",
            self.CRIPTO: "Dólar cripto (precio implícito en exchanges de criptomonedas)",
            self.TARJETA: "Dólar tarjeta (oficial + impuestos PAIS y ganancias)",
            self.MAYORISTA: "Dólar mayorista (interbancario, grandes volúmenes)",
            self.SOLIDARIO: "Dólar solidario (oficial + impuesto PAIS, para consumo)",
            self.BOLSA: "Dólar bolsa (similar a MEP, vía diferentes bonos)",
            self.TURISTA: "Dólar turista (para gastos en el exterior)",
        }
        return descripciones[self]

    def es_regulado(self) -> bool:
        """
        Indica si el tipo de dólar está regulado por el BCRA.

        Returns:
            True si está regulado, False si es de mercado libre/paralelo
        """
        regulados = {
            self.OFICIAL,
            self.MAYORISTA,
            self.TARJETA,
            self.SOLIDARIO,
            self.TURISTA,
        }
        return self in regulados

    def permite_compra_fisica(self) -> bool:
        """
        Indica si se puede comprar billetes físicos a este tipo de cambio.

        Returns:
            True si se pueden adquirir billetes físicos
        """
        con_billetes = {
            self.OFICIAL,
            self.BLUE,
            self.TARJETA,
            self.SOLIDARIO,
            self.TURISTA,
        }
        return self in con_billetes

    def es_paralelo(self) -> bool:
        """
        Indica si es un tipo de cambio paralelo/alternativo al oficial.

        Returns:
            True si es paralelo (blue, MEP, CCL, cripto)
        """
        paralelos = {
            self.BLUE,
            self.MEP,
            self.CCL,
            self.CRIPTO,
            self.BOLSA,
        }
        return self in paralelos

    @classmethod
    def desde_string(cls, valor: str) -> "TipoDolar":
        """
        Crea un TipoDolar desde un string, con normalización.

        Args:
            valor: String con el tipo de dólar (case-insensitive)

        Returns:
            TipoDolar correspondiente

        Raises:
            ValueError: Si el string no corresponde a ningún tipo conocido

        Example:
            >>> TipoDolar.desde_string("BLUE")  # TipoDolar.BLUE
            >>> TipoDolar.desde_string("mep")   # TipoDolar.MEP
            >>> TipoDolar.desde_string("MEP")   # TipoDolar.MEP
        """
        valor_normalizado = valor.lower().strip()
        try:
            return cls(valor_normalizado)
        except ValueError:
            tipos_validos = ", ".join(t.value for t in cls)
            raise ValueError(
                f"Tipo de dólar desconocido: '{valor}'. "
                f"Tipos válidos: {tipos_validos}"
            ) from None

    def __str__(self) -> str:
        """Representación en string (usa el value)."""
        return self.value

    def __repr__(self) -> str:
        """Representación técnica."""
        return f"TipoDolar.{self.name}"
