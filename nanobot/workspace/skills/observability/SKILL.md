---
name: observability
description: Use observability tools (VictoriaLogs, VictoriaTraces) to investigate errors and traces
always: true
---

# Observability Skill

Use observability MCP tools to investigate errors, failures, and performance issues in the LMS backend and other services.

## Available Tools

The following `mcp_obs_*` tools are available via the observability MCP server:

- **logs_search**: Search VictoriaLogs with a LogsQL query. Useful field names: `service.name`, `severity`, `event`, `trace_id`.
  - Example: `_time:10m service.name:"Learning Management Service" severity:ERROR`
- **logs_error_count**: Count errors per service over a time window (default 60 minutes).
- **traces_list**: List recent traces for a service.
- **traces_get**: Fetch a specific trace by ID and show the span hierarchy.

## Strategy

### When the user asks about errors or failures

1. Start with `logs_error_count` scoped to the LMS backend and a narrow time window (e.g., 10 minutes)
2. If errors are found, use `logs_search` with a focused query to get details and extract `trace_id` values
3. If a `trace_id` is found in the logs, use `traces_get` to inspect the failing request path
4. Summarize findings concisely — don't dump raw JSON

### When the user asks about performance

1. Use `traces_list` to find recent traces for the relevant service
2. Use `traces_get` with a specific trace ID to inspect span durations
3. Report which step took the longest

### General principles

- Always scope queries to a narrow time window (e.g., `_time:10m`) to avoid noise from unrelated historical errors
- Prefer the LMS backend service name: `"Learning Management Service"`
- Keep responses concise and focused on what the user asked for
- Format findings clearly: use bullet points, percentages, and brief explanations
- Don't call tools that weren't requested
