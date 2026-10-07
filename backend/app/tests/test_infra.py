import pytest
import asyncio
import time
from app.infra.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException, CircuitState
from app.infra.resilience.rate_limiter import RateLimiter
from app.infra.telemetry.metrics import MetricsCollector


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    cb = CircuitBreaker("test_provider", failure_threshold=2, recovery_timeout=0.1)

    async def failing_call():
        raise ValueError("Provider down")

    # Call 1 (failure)
    with pytest.raises(ValueError):
        await cb.call(failing_call)
    assert cb.state == CircuitState.CLOSED

    # Call 2 (trips circuit)
    with pytest.raises(ValueError):
        await cb.call(failing_call)
    assert cb.state == CircuitState.OPEN

    # Call 3 (fast fails with CircuitBreakerOpenException)
    with pytest.raises(CircuitBreakerOpenException):
        await cb.call(failing_call)

    # Wait for recovery timeout
    await asyncio.sleep(0.12)

    # Call 4 (success restores to CLOSED)
    async def healthy_call():
        return "OK"

    res = await cb.call(healthy_call)
    assert res == "OK"
    assert cb.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_rate_limiter():
    key = "user_test_limit"
    # Allow 2 requests per window
    allowed1, rem1, _ = await RateLimiter.check_rate_limit(key, max_requests=2, window_seconds=10)
    assert allowed1 is True

    allowed2, rem2, _ = await RateLimiter.check_rate_limit(key, max_requests=2, window_seconds=10)
    assert allowed2 is True

    allowed3, rem3, _ = await RateLimiter.check_rate_limit(key, max_requests=2, window_seconds=10)
    assert allowed3 is False
    assert rem3 == 0


def test_metrics_prometheus_formatting():
    MetricsCollector.record_http_request("GET", "/api/v1/notifications", 200, 12.5)
    MetricsCollector.record_mcp_tool_call("search_messages", "READ", "SUCCESS")
    prom_str = MetricsCollector.format_prometheus()
    assert "http_requests_total" in prom_str
    assert "mcp_tool_executions_total" in prom_str
    assert 'tool="search_messages"' in prom_str
