"""Query VictoriaLogs and VictoriaTraces for observability data."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from .settings import settings


# ---------------------------------------------------------------------------
# VictoriaLogs helpers
# ---------------------------------------------------------------------------

async def _vlogs_get(path: str, params: dict[str, str] | None = None, limit: int = 100) -> str:
    """GET against VictoriaLogs /select/logsql/query."""
    url = f"{settings.nanobot_victorialogs_url}{path}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params={**(params or {}), "limit": str(limit)})
        resp.raise_for_status()
        return resp.text


async def _vlogs_post(path: str, body: str) -> str:
    """POST against VictoriaLogs."""
    url = f"{settings.nanobot_victorialogs_url}{path}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, content=body, headers={"Content-Type": "text/plain"})
        resp.raise_for_status()
        return resp.text


# ---------------------------------------------------------------------------
# VictoriaTraces helpers (Jaeger-compatible API)
# ---------------------------------------------------------------------------

async def _vtraces_get(path: str, params: dict[str, str] | None = None) -> dict:
    """GET against VictoriaTraces Jaeger-compatible API."""
    url = f"{settings.nanobot_victoriatraces_url}{path}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Log tools
# ---------------------------------------------------------------------------

async def logs_search(query: str = "", limit: int = 20) -> str:
    """Search VictoriaLogs with a LogsQL query.

    Useful field names in this stack:
    - `service.name` — service identifier (e.g. "Learning Management Service")
    - `severity` — log level (INFO, ERROR, WARNING, …)
    - `event` — event name (e.g. "db_query", "request_started")
    - `trace_id` — distributed trace identifier

    Examples:
    - `_time:10m service.name:"Learning Management Service" severity:ERROR`
    - `_time:1h event:db_query`
    """
    if not query.strip():
        query = "_time:1h severity:ERROR"
    raw = await _vlogs_get("/select/logsql/query", {"query": query}, limit=limit)
    lines = [line for line in raw.strip().split("\n") if line.strip()]
    if not lines:
        return "No log entries found for the given query."
    results = []
    for line in lines[:limit]:
        try:
            entry = json.loads(line)
            results.append(
                f"  time={entry.get('_time', '?')} "
                f"severity={entry.get('severity', '?')} "
                f"service={entry.get('service.name', '?')} "
                f"event={entry.get('event', '?')} "
                f"msg={entry.get('message', entry.get('msg', ''))}"
            )
            if "trace_id" in entry:
                results[-1] += f" trace_id={entry['trace_id']}"
        except json.JSONDecodeError:
            results.append(line[:200])
    return f"Found {len(results)} log entries:\n" + "\n".join(results)


async def logs_error_count(service: str = "", minutes: int = 60) -> str:
    """Count errors per service over a time window.

    If *service* is given, only count errors for that service.
    """
    window = f"_time:{minutes}m"
    base = f"{window} severity:ERROR"
    query = f'{base} service.name:"{service}"' if service else base
    raw = await _vlogs_get("/select/logsql/query", {"query": query}, limit=5000)
    lines = [line for line in raw.strip().split("\n") if line.strip()]
    count = len(lines)
    if service:
        return f"Found {count} error(s) for service '{service}' in the last {minutes} minutes."
    # Group by service
    by_service: dict[str, int] = {}
    for line in lines:
        try:
            entry = json.loads(line)
            svc = entry.get("service.name", "unknown")
            by_service[svc] = by_service.get(svc, 0) + 1
        except json.JSONDecodeError:
            by_service["unknown"] = by_service.get("unknown", 0) + 1
    parts = [f"Found {count} total error(s) in the last {minutes} minutes:"]
    for svc, n in sorted(by_service.items(), key=lambda x: -x[1]):
        parts.append(f"  - {svc}: {n}")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Trace tools
# ---------------------------------------------------------------------------

async def traces_list(service: str = "", limit: int = 10) -> str:
    """List recent traces for a service.

    Uses the Jaeger-compatible API of VictoriaTraces.
    """
    params: dict[str, str] = {"limit": str(limit)}
    if service:
        params["service"] = service
    data = await _vtraces_get("/select/jaeger/api/traces", params)
    traces = data.get("data", [])
    if not traces:
        return "No traces found."
    lines = [f"Found {len(traces)} trace(s):"]
    for t in traces[:limit]:
        trace_id = t.get("traceID", "?")
        spans = t.get("spans", [])
        duration_ms = _trace_duration_ms(t)
        services = sorted({s.get("processID", "") for s in spans})
        lines.append(
            f"  trace_id={trace_id} "
            f"spans={len(spans)} "
            f"duration={duration_ms}ms "
            f"services={', '.join(services[:5])}"
        )
    return "\n".join(lines)


async def traces_get(trace_id: str) -> str:
    """Fetch a specific trace by ID and show the span hierarchy.

    The *trace_id* should be a hex string (e.g. from a log entry).
    """
    data = await _vtraces_get(f"/select/jaeger/api/traces/{trace_id}")
    traces = data.get("data", [])
    if not traces:
        return f"No trace found with ID {trace_id}."
    t = traces[0]
    spans = t.get("spans", [])
    lines = [f"Trace {trace_id} — {len(spans)} span(s):"]
    for s in sorted(spans, key=lambda x: x.get("startTime", 0)):
        indent = "  " * (1 + s.get("depth", 0))
        duration = s.get("duration", 0) / 1000  # µs → ms
        op = s.get("operationName", "?")
        tags = s.get("tags", [])
        error_tag = any(
            tag.get("key") == "error" and tag.get("value")
            for tag in tags
            if isinstance(tag, dict)
        )
        flag = " ⚠️ ERROR" if error_tag else ""
        lines.append(f"{indent}{op} ({duration:.1f}ms){flag}")
    return "\n".join(lines)


def _trace_duration_ms(trace: dict) -> float:
    """Return total trace duration in milliseconds."""
    spans = trace.get("spans", [])
    if not spans:
        return 0
    starts = [s.get("startTime", 0) for s in spans]
    ends = [s.get("startTime", 0) + s.get("duration", 0) for s in spans]
    return (max(ends) - min(starts)) / 1000 if starts and ends else 0
