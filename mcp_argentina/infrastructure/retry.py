"""
Retry utilities with exponential backoff.

Provides decorators and helpers for resilient API calls.
"""

import asyncio
import functools
from collections.abc import Callable
from typing import Any, TypeVar

from mcp_argentina.infrastructure.errors import (
    APIError,
    APIRateLimitError,
    APITimeoutError,
    APIUnavailableError,
)
from mcp_argentina.infrastructure.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of attempts
            initial_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


DEFAULT_RETRY_CONFIG = RetryConfig()


def calculate_delay(
    attempt: int,
    config: RetryConfig,
) -> float:
    """Calculate delay for a retry attempt."""
    import random

    delay = config.initial_delay * (config.exponential_base**attempt)
    delay = min(delay, config.max_delay)

    if config.jitter:
        delay *= 0.5 + random.random()

    return delay


def is_retryable(error: Exception) -> bool:
    """Determine if an error is retryable."""
    if isinstance(error, APITimeoutError):
        return True
    if isinstance(error, APIUnavailableError):
        return True
    if isinstance(error, APIRateLimitError):
        return True
    if isinstance(error, (asyncio.TimeoutError, ConnectionError, OSError)):
        return True
    return False


async def retry_async(
    func: Callable[..., Any],
    *args: Any,
    config: RetryConfig | None = None,
    **kwargs: Any,
) -> Any:
    """
    Execute an async function with retry logic.

    Args:
        func: Async function to call
        *args: Positional arguments
        config: Retry configuration
        **kwargs: Keyword arguments

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    config = config or DEFAULT_RETRY_CONFIG
    last_error: Exception | None = None

    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_error = e

            if not is_retryable(e):
                logger.warning(
                    f"Non-retryable error: {type(e).__name__}: {e}",
                    extra={"attempt": attempt + 1, "error_type": type(e).__name__},
                )
                raise

            if attempt < config.max_attempts - 1:
                delay = calculate_delay(attempt, config)

                # Respect Retry-After header if present
                if isinstance(e, APIRateLimitError) and e.retry_after:
                    delay = max(delay, e.retry_after)

                logger.warning(
                    f"Retry attempt {attempt + 1}/{config.max_attempts} after {delay:.1f}s: {e}",
                    extra={
                        "attempt": attempt + 1,
                        "delay": delay,
                        "error_type": type(e).__name__,
                    },
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"All {config.max_attempts} attempts failed: {e}",
                    extra={
                        "attempts": config.max_attempts,
                        "error_type": type(e).__name__,
                    },
                )

    if last_error:
        raise last_error
    raise RuntimeError("Unexpected retry state")


def with_retry(
    config: RetryConfig | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for adding retry logic to async functions.

    Args:
        config: Retry configuration

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(RetryConfig(max_attempts=5))
        async def fetch_data():
            ...
    """
    _config = config or DEFAULT_RETRY_CONFIG

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await retry_async(func, *args, config=_config, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


class CircuitBreaker:
    """
    Circuit breaker for preventing cascade failures.

    States:
    - CLOSED: Normal operation
    - OPEN: Failing fast, not making requests
    - HALF_OPEN: Testing if service recovered
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before trying half-open
            half_open_max_calls: Calls allowed in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = self.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0
        self._half_open_calls = 0

    @property
    def state(self) -> str:
        """Current circuit state."""
        import time

        if self._state == self.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = self.HALF_OPEN
                self._half_open_calls = 0

        return self._state

    def record_success(self) -> None:
        """Record a successful call."""
        if self._state == self.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max_calls:
                self._state = self.CLOSED
                self._failure_count = 0
                logger.info("Circuit breaker closed")
        elif self._state == self.CLOSED:
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        import time

        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == self.HALF_OPEN:
            self._state = self.OPEN
            logger.warning("Circuit breaker reopened after half-open failure")
        elif self._failure_count >= self.failure_threshold:
            self._state = self.OPEN
            logger.warning(f"Circuit breaker opened after {self._failure_count} failures")

    def can_execute(self) -> bool:
        """Check if a call can be made."""
        state = self.state  # Triggers state check
        if state == self.CLOSED:
            return True
        if state == self.HALF_OPEN:
            return self._half_open_calls < self.half_open_max_calls
        return False

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function through the circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            APIError: If circuit is open
            Exception: From the function
        """
        if not self.can_execute():
            raise APIError(
                "Service unavailable (circuit breaker open)",
                source="circuit_breaker",
            )

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            if is_retryable(e):
                self.record_failure()
            raise
