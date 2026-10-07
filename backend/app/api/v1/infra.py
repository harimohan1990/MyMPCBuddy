from fastapi import APIRouter, Response
from app.infra.telemetry.metrics import MetricsCollector
from app.infra.resilience.circuit_breaker import CircuitBreakerRegistry

router = APIRouter(prefix="/infra", tags=["Infrastructure & Observability"])


@router.get("/metrics")
async def get_metrics():
    """Prometheus-compatible plaintext metrics endpoint."""
    content = MetricsCollector.format_prometheus()
    return Response(content=content, media_type="text/plain")


@router.get("/summary")
async def get_infra_summary():
    """Aggregated infrastructure health, metrics summary, and circuit breaker states."""
    return {
        "metrics": MetricsCollector.get_summary(),
        "circuit_breakers": CircuitBreakerRegistry.all_statuses(),
    }
