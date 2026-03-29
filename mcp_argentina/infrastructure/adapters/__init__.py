"""Infrastructure adapters."""

from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter
from mcp_argentina.infrastructure.adapters.cached_repository import CachedCotizacionRepository
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter

__all__ = [
    "CacheAdapter",
    "DolarAPIAdapter",
    "CachedCotizacionRepository",
]
