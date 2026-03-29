"""
Cache adapter in-memory con TTL para cotizaciones.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Generic, TypeVar

from mcp_argentina.domain.entities.cotizacion import Cotizacion

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """
    Entrada de cache con timestamp y TTL.
    """

    value: T
    created_at: datetime
    ttl_seconds: int

    def is_expired(self) -> bool:
        """Verifica si la entrada expiró."""
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() > expiry_time


class CacheAdapter:
    """
    Cache in-memory simple con TTL por entrada.

    Thread-safe mediante asyncio.Lock.
    Ideal para evitar rate limiting en APIs externas.
    """

    def __init__(self, default_ttl: int = 60):
        """
        Inicializa el cache.

        Args:
            default_ttl: TTL por defecto en segundos (default: 60)
        """
        self._cache: dict[str, CacheEntry[Any]] = {}
        self._lock = asyncio.Lock()
        self._default_ttl = default_ttl

    async def get(self, key: str) -> Any | None:
        """
        Obtiene un valor del cache si existe y no expiró.

        Args:
            key: Clave de cache

        Returns:
            Valor cacheado o None si no existe o expiró
        """
        async with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return None

            if entry.is_expired():
                del self._cache[key]
                return None

            return entry.value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Almacena un valor en cache con TTL.

        Args:
            key: Clave de cache
            value: Valor a almacenar
            ttl: TTL en segundos (default: usa default_ttl)
        """
        async with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                created_at=datetime.utcnow(),
                ttl_seconds=ttl or self._default_ttl,
            )

    async def delete(self, key: str) -> None:
        """
        Elimina una entrada del cache.

        Args:
            key: Clave de cache
        """
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        """Limpia todo el cache."""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self) -> int:
        """
        Elimina todas las entradas expiradas.

        Returns:
            Cantidad de entradas eliminadas
        """
        async with self._lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    async def size(self) -> int:
        """
        Retorna la cantidad de entradas en cache (sin contar expiradas).

        Returns:
            Número de entradas válidas
        """
        async with self._lock:
            return sum(1 for entry in self._cache.values() if not entry.is_expired())

    def _make_key(self, prefix: str, *args: str) -> str:
        """
        Helper para generar keys compuestas.

        Args:
            prefix: Prefijo (ej: "dolar", "moneda")
            *args: Argumentos adicionales

        Returns:
            Key compuesta (ej: "dolar:blue")
        """
        return ":".join([prefix, *args])

    # Helpers específicos para cotizaciones

    async def get_dolar(self, casa: str) -> Cotizacion | None:
        """Obtiene cotización de dólar cacheada."""
        return await self.get(self._make_key("dolar", casa))

    async def set_dolar(self, casa: str, cotizacion: Cotizacion, ttl: int | None = None) -> None:
        """Almacena cotización de dólar."""
        await self.set(self._make_key("dolar", casa), cotizacion, ttl)

    async def get_todas_cotizaciones(self) -> list[Cotizacion] | None:
        """Obtiene lista completa de cotizaciones cacheada."""
        return await self.get("dolares:todas")

    async def set_todas_cotizaciones(
        self, cotizaciones: list[Cotizacion], ttl: int | None = None
    ) -> None:
        """Almacena lista completa de cotizaciones."""
        await self.set("dolares:todas", cotizaciones, ttl)

    async def get_moneda(self, moneda: str) -> Cotizacion | None:
        """Obtiene cotización de moneda cacheada."""
        return await self.get(self._make_key("moneda", moneda.lower()))

    async def set_moneda(self, moneda: str, cotizacion: Cotizacion, ttl: int | None = None) -> None:
        """Almacena cotización de moneda."""
        await self.set(self._make_key("moneda", moneda.lower()), cotizacion, ttl)
