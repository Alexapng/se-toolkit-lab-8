"""MCP server for observability tools (VictoriaLogs + VictoriaTraces)."""

from mcp.server.fastmcp import FastMCP

from . import observability

mcp = FastMCP("mcp-obs")


@mcp.tool()
async def logs_search(query: str = "", limit: int = 20) -> str:
    """Search VictoriaLogs with a LogsQL query.

    Useful field names: `service.name`, `severity`, `event`, `trace_id`.
    Examples:
    - `_time:10m service.name:"Learning Management Service" severity:ERROR`
    - `_time:1h event:db_query`
    """
    return await observability.logs_search(query=query, limit=limit)


@mcp.tool()
async def logs_error_count(service: str = "", minutes: int = 60) -> str:
    """Count errors per service over a time window (default 60 minutes)."""
    return await observability.logs_error_count(service=service, minutes=minutes)


@mcp.tool()
async def traces_list(service: str = "", limit: int = 10) -> str:
    """List recent traces for a service (Jaeger-compatible API)."""
    return await observability.traces_list(service=service, limit=limit)


@mcp.tool()
async def traces_get(trace_id: str) -> str:
    """Fetch a specific trace by ID and show the span hierarchy."""
    return await observability.traces_get(trace_id=trace_id)
