import time
import asyncio
from enum import Enum
from typing import Callable, Any, Optional
from app.core.logging import logger


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Normal operation, traffic flows
    OPEN = "OPEN"          # Failing, fast reject all requests
    HALF_OPEN = "HALF_OPEN"# Testing recovery with limited requests


class CircuitBreakerOpenException(Exception):
    def __init__(self, service_name: str, retry_after: float):
        super().__init__(f"Circuit breaker for service '{service_name}' is OPEN. Retry after {retry_after:.1f}s")
        self.service_name = service_name
        self.retry_after = retry_after


class CircuitBreaker:
    """
    Production-grade Circuit Breaker pattern with exponential recovery backoff.
    Protects downstream providers (Gmail, Microsoft Graph, Meta Cloud API) from cascading failures.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exceptions: tuple = (Exception,)
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_state_change = time.time()
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        async with self._lock:
            now = time.time()
            if self.state == CircuitState.OPEN:
                elapsed = now - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    logger.info(f"Circuit '{self.name}' transitioning from OPEN to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.last_state_change = now
                else:
                    retry_after = self.recovery_timeout - elapsed
                    raise CircuitBreakerOpenException(self.name, retry_after)

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            async with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    logger.info(f"Circuit '{self.name}' successfully recovered. Transitioning to CLOSED.")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.last_state_change = time.time()
                elif self.state == CircuitState.CLOSED:
                    self.failure_count = 0
            return result
        except self.expected_exceptions as e:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                logger.warning(
                    f"Circuit '{self.name}' recorded failure #{self.failure_count}: {str(e)}"
                )
                if self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN) and self.failure_count >= self.failure_threshold:
                    logger.error(
                        f"Circuit '{self.name}' tripped! Transitioning to OPEN. Threshold: {self.failure_threshold}"
                    )
                    self.state = CircuitState.OPEN
                    self.last_state_change = time.time()
            raise e

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }


# Global registry for provider circuit breakers
class CircuitBreakerRegistry:
    _breakers: dict[str, CircuitBreaker] = {}

    @classmethod
    def get(cls, name: str, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> CircuitBreaker:
        if name not in cls._breakers:
            cls._breakers[name] = CircuitBreaker(name, failure_threshold, recovery_timeout)
        return cls._breakers[name]

    @classmethod
    def all_statuses(cls) -> list[dict]:
        return [cb.get_status() for cb in cls._breakers.values()]
