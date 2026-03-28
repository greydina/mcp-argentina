"""
Adapters de infraestructura para APIs externas.
"""

from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter

__all__ = ["DolarAPIAdapter", "CacheAdapter"]
