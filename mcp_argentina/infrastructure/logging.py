"""
Structured logging configuration for MCP Argentina.

Provides JSON logging for production and human-readable for development.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add context fields from record
        for key in ["request_id", "tool", "duration_ms", "status", "error_type"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        return json.dumps(log_data, ensure_ascii=False, default=str)


class HumanFormatter(logging.Formatter):
    """Human-readable formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for humans."""
        color = self.COLORS.get(record.levelname, "")
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Base message
        msg = f"{color}[{timestamp}] {record.levelname:8}{self.RESET} {record.getMessage()}"

        # Add context if present
        context_parts = []
        for key in ["tool", "duration_ms", "status"]:
            if hasattr(record, key):
                context_parts.append(f"{key}={getattr(record, key)}")

        if context_parts:
            msg += f" ({', '.join(context_parts)})"

        # Add exception
        if record.exc_info:
            msg += f"\n{self.formatException(record.exc_info)}"

        return msg


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    name: str = "mcp_argentina",
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format (for production)
        name: Logger name

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stderr)

    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(HumanFormatter())

    logger.addHandler(handler)

    # Don't propagate to root logger
    logger.propagate = False

    return logger


# Default logger instance
logger = setup_logging()


def get_logger(name: str = "mcp_argentina") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class LogContext:
    """Context manager for structured logging with timing."""

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        **extra: Any,
    ):
        self.logger = logger
        self.operation = operation
        self.extra = extra
        self.start_time: float = 0

    def __enter__(self) -> "LogContext":
        import time

        self.start_time = time.perf_counter()
        self.logger.debug(
            f"Starting {self.operation}",
            extra={"tool": self.operation, **self.extra},
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        import time

        duration_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type:
            self.logger.error(
                f"Failed {self.operation}: {exc_val}",
                extra={
                    "tool": self.operation,
                    "duration_ms": round(duration_ms, 2),
                    "status": "error",
                    "error_type": exc_type.__name__,
                    **self.extra,
                },
                exc_info=True,
            )
        else:
            self.logger.info(
                f"Completed {self.operation}",
                extra={
                    "tool": self.operation,
                    "duration_ms": round(duration_ms, 2),
                    "status": "success",
                    **self.extra,
                },
            )
