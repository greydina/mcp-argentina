"""
Servicio para generar gráficos ASCII de tendencias.

No requiere dependencias externas - genera gráficos en texto plano
compatibles con cualquier terminal o chat.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class PuntoGrafico:
    """Un punto en el gráfico."""

    fecha: date
    valor: float
    etiqueta: str = ""


class GraficosService:
    """
    Genera gráficos ASCII de tendencias económicas.

    Example:
        >>> service = GraficosService()
        >>> grafico = service.generar_linea(datos, titulo="Dólar Blue")
        >>> print(grafico)
    """

    def __init__(self, ancho: int = 40, alto: int = 10):
        """
        Inicializa el servicio.

        Args:
            ancho: Ancho del gráfico en caracteres
            alto: Alto del gráfico en líneas
        """
        self.ancho = ancho
        self.alto = alto

    def generar_linea(
        self,
        datos: list[PuntoGrafico],
        titulo: str = "",
        mostrar_valores: bool = True,
    ) -> str:
        """
        Genera un gráfico de línea ASCII.

        Args:
            datos: Lista de puntos a graficar
            titulo: Título del gráfico
            mostrar_valores: Si mostrar valores en Y

        Returns:
            String con el gráfico ASCII
        """
        if not datos:
            return "Sin datos para graficar"

        valores = [d.valor for d in datos]
        minimo = min(valores)
        maximo = max(valores)
        rango = maximo - minimo or 1

        # Caracteres para el gráfico
        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        lineas = []

        # Título
        if titulo:
            lineas.append(f"📊 {titulo}")
            lineas.append("")

        # Valores min/max
        if mostrar_valores:
            lineas.append(f"Max: ${maximo:,.0f}")

        # Gráfico
        grafico = ""
        for punto in datos:
            normalizado = (punto.valor - minimo) / rango
            indice = min(int(normalizado * (len(chars) - 1)), len(chars) - 1)
            grafico += chars[indice]

        lineas.append(grafico)

        if mostrar_valores:
            lineas.append(f"Min: ${minimo:,.0f}")

        # Fechas
        if len(datos) >= 2:
            fecha_inicio = datos[0].fecha.strftime("%d/%m")
            fecha_fin = datos[-1].fecha.strftime("%d/%m")
            espacios = len(grafico) - len(fecha_inicio) - len(fecha_fin)
            lineas.append(f"{fecha_inicio}{' ' * max(espacios, 1)}{fecha_fin}")

        # Variación
        if len(datos) >= 2:
            variacion = ((datos[-1].valor - datos[0].valor) / datos[0].valor) * 100
            emoji = "📈" if variacion > 0 else "📉" if variacion < 0 else "➡️"
            lineas.append(f"{emoji} {variacion:+.1f}%")

        return "\n".join(lineas)

    def generar_barras(
        self,
        datos: list[tuple[str, float]],
        titulo: str = "",
        ancho_barra: int = 20,
    ) -> str:
        """
        Genera un gráfico de barras horizontales.

        Args:
            datos: Lista de (etiqueta, valor)
            titulo: Título del gráfico
            ancho_barra: Ancho máximo de las barras

        Returns:
            String con el gráfico ASCII
        """
        if not datos:
            return "Sin datos para graficar"

        maximo = max(v for _, v in datos)
        lineas = []

        if titulo:
            lineas.append(f"📊 {titulo}")
            lineas.append("")

        for etiqueta, valor in datos:
            normalizado = valor / maximo if maximo > 0 else 0
            longitud = int(normalizado * ancho_barra)
            barra = "█" * longitud + "░" * (ancho_barra - longitud)
            lineas.append(f"{etiqueta:>8}: {barra} {valor:,.0f}")

        return "\n".join(lineas)

    def generar_comparacion(
        self,
        valor1: float,
        valor2: float,
        etiqueta1: str = "Antes",
        etiqueta2: str = "Ahora",
        titulo: str = "",
    ) -> str:
        """
        Genera una comparación visual entre dos valores.

        Args:
            valor1: Primer valor
            valor2: Segundo valor
            etiqueta1: Etiqueta del primer valor
            etiqueta2: Etiqueta del segundo valor
            titulo: Título de la comparación

        Returns:
            String con la comparación
        """
        variacion = ((valor2 - valor1) / valor1) * 100 if valor1 > 0 else 0
        emoji = "📈" if variacion > 0 else "📉" if variacion < 0 else "➡️"

        lineas = []
        if titulo:
            lineas.append(f"📊 {titulo}")
            lineas.append("")

        lineas.append(f"{etiqueta1}: ${valor1:,.0f}")
        lineas.append(f"{etiqueta2}: ${valor2:,.0f}")
        lineas.append(f"{emoji} Variación: {variacion:+.1f}%")

        return "\n".join(lineas)

    def generar_tabla(
        self,
        datos: list[dict],
        columnas: list[str],
        titulo: str = "",
    ) -> str:
        """
        Genera una tabla ASCII.

        Args:
            datos: Lista de diccionarios con los datos
            columnas: Lista de claves a mostrar
            titulo: Título de la tabla

        Returns:
            String con la tabla
        """
        if not datos or not columnas:
            return "Sin datos"

        lineas = []
        if titulo:
            lineas.append(f"📊 {titulo}")
            lineas.append("")

        # Calcular anchos
        anchos = {}
        for col in columnas:
            valores = [str(d.get(col, "")) for d in datos]
            anchos[col] = max(len(col), max(len(v) for v in valores))

        # Header
        header = " | ".join(col.ljust(anchos[col]) for col in columnas)
        lineas.append(header)
        lineas.append("-" * len(header))

        # Filas
        for d in datos:
            fila = " | ".join(str(d.get(col, "")).ljust(anchos[col]) for col in columnas)
            lineas.append(fila)

        return "\n".join(lineas)
