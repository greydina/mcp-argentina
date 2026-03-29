"""
Servicio de alertas para cambios significativos en cotizaciones.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from mcp_argentina.infrastructure.adapters.cached_repository import (
    CachedCotizacionRepository,
)


class TipoAlerta(Enum):
    """Tipos de alerta."""

    SUBIDA = "subida"
    BAJADA = "bajada"
    UMBRAL_SUPERADO = "umbral_superado"
    UMBRAL_INFERIOR = "umbral_inferior"


@dataclass
class Alerta:
    """Representa una alerta generada."""

    tipo: TipoAlerta
    cotizacion: str  # "blue", "oficial", etc.
    valor_actual: float
    valor_referencia: float
    variacion_porcentual: float
    mensaje: str
    timestamp: datetime


@dataclass
class ConfiguracionAlerta:
    """Configuración de una alerta."""

    cotizacion: str
    umbral_porcentual: float | None = None  # Variación % que dispara alerta
    valor_minimo: float | None = None  # Alerta si baja de este valor
    valor_maximo: float | None = None  # Alerta si sube de este valor
    activa: bool = True


AlertaCallback = Callable[[Alerta], Awaitable[None]]


class AlertasService:
    """
    Servicio para monitorear y generar alertas de cotizaciones.

    Example:
        >>> service = AlertasService(repository)
        >>> service.configurar_alerta(ConfiguracionAlerta(
        ...     cotizacion="blue",
        ...     umbral_porcentual=5.0
        ... ))
        >>> alertas = await service.verificar_alertas()
    """

    def __init__(self, repository: CachedCotizacionRepository):
        """
        Inicializa el servicio.

        Args:
            repository: Repositorio de cotizaciones
        """
        self._repository = repository
        self._configuraciones: list[ConfiguracionAlerta] = []
        self._valores_referencia: dict[str, float] = {}
        self._callbacks: list[AlertaCallback] = []

    def configurar_alerta(self, config: ConfiguracionAlerta) -> None:
        """
        Configura una nueva alerta.

        Args:
            config: Configuración de la alerta
        """
        # Remover configuración existente para la misma cotización
        self._configuraciones = [
            c for c in self._configuraciones if c.cotizacion != config.cotizacion
        ]
        self._configuraciones.append(config)

    def registrar_callback(self, callback: AlertaCallback) -> None:
        """
        Registra un callback para cuando se genere una alerta.

        Args:
            callback: Función async a llamar con la alerta
        """
        self._callbacks.append(callback)

    async def verificar_alertas(self) -> list[Alerta]:
        """
        Verifica todas las alertas configuradas.

        Returns:
            Lista de alertas generadas
        """
        alertas = []

        for config in self._configuraciones:
            if not config.activa:
                continue

            try:
                alerta = await self._verificar_alerta(config)
                if alerta:
                    alertas.append(alerta)
                    for callback in self._callbacks:
                        await callback(alerta)
            except Exception:
                # Log error pero continuar con otras alertas
                continue

        return alertas

    async def _verificar_alerta(self, config: ConfiguracionAlerta) -> Alerta | None:
        """Verifica una alerta específica."""
        cotizacion = await self._repository.obtener_dolar(config.cotizacion)
        valor_actual = float(cotizacion.venta.valor)

        # Obtener valor de referencia
        valor_ref = self._valores_referencia.get(config.cotizacion, valor_actual)
        self._valores_referencia[config.cotizacion] = valor_actual

        # Calcular variación
        variacion = ((valor_actual - valor_ref) / valor_ref * 100) if valor_ref > 0 else 0

        # Verificar umbral porcentual
        if config.umbral_porcentual and abs(variacion) >= config.umbral_porcentual:
            tipo = TipoAlerta.SUBIDA if variacion > 0 else TipoAlerta.BAJADA
            return Alerta(
                tipo=tipo,
                cotizacion=config.cotizacion,
                valor_actual=valor_actual,
                valor_referencia=valor_ref,
                variacion_porcentual=round(variacion, 2),
                mensaje=self._generar_mensaje(tipo, config.cotizacion, valor_actual, variacion),
                timestamp=datetime.now(),
            )

        # Verificar valor máximo
        if config.valor_maximo and valor_actual > config.valor_maximo:
            return Alerta(
                tipo=TipoAlerta.UMBRAL_SUPERADO,
                cotizacion=config.cotizacion,
                valor_actual=valor_actual,
                valor_referencia=config.valor_maximo,
                variacion_porcentual=0,
                mensaje=f"⚠️ Dólar {config.cotizacion.upper()} superó ${config.valor_maximo:,.0f} (actual: ${valor_actual:,.0f})",
                timestamp=datetime.now(),
            )

        # Verificar valor mínimo
        if config.valor_minimo and valor_actual < config.valor_minimo:
            return Alerta(
                tipo=TipoAlerta.UMBRAL_INFERIOR,
                cotizacion=config.cotizacion,
                valor_actual=valor_actual,
                valor_referencia=config.valor_minimo,
                variacion_porcentual=0,
                mensaje=f"⚠️ Dólar {config.cotizacion.upper()} cayó bajo ${config.valor_minimo:,.0f} (actual: ${valor_actual:,.0f})",
                timestamp=datetime.now(),
            )

        return None

    def _generar_mensaje(
        self, tipo: TipoAlerta, cotizacion: str, valor: float, variacion: float
    ) -> str:
        """Genera mensaje de alerta."""
        emoji = "📈" if tipo == TipoAlerta.SUBIDA else "📉"
        direccion = "subió" if tipo == TipoAlerta.SUBIDA else "bajó"
        return (
            f"{emoji} Dólar {cotizacion.upper()} {direccion} {abs(variacion):.1f}% (${valor:,.0f})"
        )

    def obtener_configuraciones(self) -> list[ConfiguracionAlerta]:
        """Retorna las configuraciones activas."""
        return [c for c in self._configuraciones if c.activa]

    def desactivar_alerta(self, cotizacion: str) -> bool:
        """
        Desactiva una alerta.

        Args:
            cotizacion: Tipo de cotización

        Returns:
            True si se desactivó, False si no existía
        """
        for config in self._configuraciones:
            if config.cotizacion == cotizacion:
                config = ConfiguracionAlerta(
                    cotizacion=config.cotizacion,
                    umbral_porcentual=config.umbral_porcentual,
                    valor_minimo=config.valor_minimo,
                    valor_maximo=config.valor_maximo,
                    activa=False,
                )
                return True
        return False
