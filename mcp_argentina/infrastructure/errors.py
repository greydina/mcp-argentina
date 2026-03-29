"""
Custom exceptions for MCP Argentina.

Provides a hierarchy of errors for better error handling and reporting.
"""

from typing import Any


class MCPArgentinaError(Exception):
    """Base exception for all MCP Argentina errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "UNKNOWN_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


# API Errors
class APIError(MCPArgentinaError):
    """Error communicating with external API."""

    def __init__(
        self,
        message: str,
        *,
        source: str = "unknown",
        status_code: int | None = None,
        url: str | None = None,
    ):
        super().__init__(
            message,
            code="API_ERROR",
            details={
                "source": source,
                "status_code": status_code,
                "url": url,
            },
        )
        self.source = source
        self.status_code = status_code
        self.url = url


class APITimeoutError(APIError):
    """API request timed out."""

    def __init__(self, source: str, url: str | None = None):
        super().__init__(
            f"Request to {source} timed out",
            source=source,
            url=url,
        )
        self.code = "API_TIMEOUT"


class APIRateLimitError(APIError):
    """API rate limit exceeded."""

    def __init__(
        self,
        source: str,
        retry_after: int | None = None,
    ):
        super().__init__(
            f"Rate limit exceeded for {source}",
            source=source,
        )
        self.code = "RATE_LIMIT"
        self.retry_after = retry_after
        self.details["retry_after"] = retry_after


class APIUnavailableError(APIError):
    """API is unavailable (5xx errors)."""

    def __init__(self, source: str, status_code: int):
        super().__init__(
            f"{source} is unavailable (HTTP {status_code})",
            source=source,
            status_code=status_code,
        )
        self.code = "API_UNAVAILABLE"


# Validation Errors
class ValidationError(MCPArgentinaError):
    """Input validation error."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: Any = None,
    ):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            details={"field": field, "value": str(value) if value else None},
        )
        self.field = field
        self.value = value


class InvalidCotizacionError(ValidationError):
    """Invalid cotización type."""

    def __init__(self, tipo: str, valid_types: list[str]):
        super().__init__(
            f"Tipo de cotización inválido: '{tipo}'. Válidos: {', '.join(valid_types)}",
            field="tipo",
            value=tipo,
        )
        self.code = "INVALID_COTIZACION"


class InvalidMonedaError(ValidationError):
    """Invalid currency code."""

    def __init__(self, moneda: str, valid_currencies: list[str]):
        super().__init__(
            f"Moneda inválida: '{moneda}'. Válidas: {', '.join(valid_currencies)}",
            field="moneda",
            value=moneda,
        )
        self.code = "INVALID_MONEDA"


# Data Errors
class DataError(MCPArgentinaError):
    """Error with data processing or availability."""

    def __init__(self, message: str, *, source: str | None = None):
        super().__init__(
            message,
            code="DATA_ERROR",
            details={"source": source},
        )
        self.source = source


class NoDataError(DataError):
    """No data available."""

    def __init__(self, resource: str, source: str | None = None):
        super().__init__(
            f"No hay datos disponibles para: {resource}",
            source=source,
        )
        self.code = "NO_DATA"


class StaleDataError(DataError):
    """Data is stale/outdated."""

    def __init__(self, resource: str, age_minutes: int):
        super().__init__(
            f"Datos de {resource} desactualizados ({age_minutes} minutos)",
        )
        self.code = "STALE_DATA"
        self.details["age_minutes"] = age_minutes


# Cache Errors
class CacheError(MCPArgentinaError):
    """Cache-related error."""

    def __init__(self, message: str):
        super().__init__(message, code="CACHE_ERROR")


def handle_http_error(
    source: str,
    status_code: int,
    url: str | None = None,
) -> APIError:
    """
    Convert HTTP status code to appropriate exception.

    Args:
        source: API source name
        status_code: HTTP status code
        url: Request URL

    Returns:
        Appropriate APIError subclass
    """
    if status_code == 429:
        return APIRateLimitError(source)
    elif status_code >= 500:
        return APIUnavailableError(source, status_code)
    else:
        return APIError(
            f"{source} returned HTTP {status_code}",
            source=source,
            status_code=status_code,
            url=url,
        )
