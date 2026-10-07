import time
from typing import Dict, Any
from collections import defaultdict


class MetricsCollector:
    """
    In-process telemetry and Prometheus metrics collector.
    Tracks API latency, MCP tool executions, provider sync performance, and security events.
    """

    _http_requests_total = defaultdict(int)
    _mcp_tool_calls_total = defaultdict(int)
    _provider_sync_total = defaultdict(int)
    _security_rejections_total = defaultdict(int)
    _request_durations = []

    @classmethod
    def record_http_request(cls, method: str, path: str, status_code: int, duration_ms: float):
        key = f'{method} {path} {status_code}'
        cls._http_requests_total[key] += 1
        if len(cls._request_durations) > 1000:
            cls._request_durations.pop(0)
        cls._request_durations.append(duration_ms)

    @classmethod
    def record_mcp_tool_call(cls, tool_name: str, permission: str, status: str):
        key = f'{tool_name} {permission} {status}'
        cls._mcp_tool_calls_total[key] += 1

    @classmethod
    def record_provider_sync(cls, provider: str, status: str):
        key = f'{provider} {status}'
        cls._provider_sync_total[key] += 1

    @classmethod
    def record_security_rejection(cls, reason: str):
        cls._security_rejections_total[reason] += 1

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        avg_latency = (
            sum(cls._request_durations) / len(cls._request_durations)
            if cls._request_durations else 0.0
        )
        return {
            "http_requests_total": dict(cls._http_requests_total),
            "mcp_tool_calls_total": dict(cls._mcp_tool_calls_total),
            "provider_sync_total": dict(cls._provider_sync_total),
            "security_rejections_total": dict(cls._security_rejections_total),
            "avg_latency_ms": round(avg_latency, 2),
            "total_requests_tracked": len(cls._request_durations),
        }

    @classmethod
    def format_prometheus(cls) -> str:
        lines = []
        lines.append("# HELP http_requests_total Total HTTP requests")
        lines.append("# TYPE http_requests_total counter")
        for key, val in cls._http_requests_total.items():
            parts = key.split()
            lines.append(f'http_requests_total{{method="{parts[0]}",path="{parts[1]}",status="{parts[2]}"}} {val}')

        lines.append("\n# HELP mcp_tool_executions_total Total MCP tool executions")
        lines.append("# TYPE mcp_tool_executions_total counter")
        for key, val in cls._mcp_tool_calls_total.items():
            parts = key.split()
            lines.append(f'mcp_tool_executions_total{{tool="{parts[0]}",permission="{parts[1]}",status="{parts[2]}"}} {val}')

        lines.append("\n# HELP provider_sync_total Total provider synchronizations")
        lines.append("# TYPE provider_sync_total counter")
        for key, val in cls._provider_sync_total.items():
            parts = key.split()
            lines.append(f'provider_sync_total{{provider="{parts[0]}",status="{parts[1]}"}} {val}')

        return "\n".join(lines) + "\n"
