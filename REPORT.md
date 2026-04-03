# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Query:** `uv run nanobot agent --logs --session cli:task1a-loop -c ./config.json -m "What is the agentic loop?"`

**Agent response:**

```
The agentic loop is the core cycle that an AI agent follows to
accomplish tasks autonomously. Here's how it works:

 1 Perceive — The agent receives input: a user request, tool output,
   or environmental signal.
 2 Reason — The agent analyzes the situation, decides what to do
   next, and plans its approach. This is where the LLM "thinks" about
   the problem.
 3 Act — The agent executes an action: calling a tool (reading a
   file, running a command, searching the web), sending a message, or
   making a decision.
 4 Observe — The agent receives the result of its action (success,
   error, data returned).
 5 Repeat — Based on the observation, the agent loops back to step 2
   — reasoning about what to do next — until the task is complete or
   a stopping condition is met.

 User Request → Perceive → Reason → Act → Observe → (loop back to
 Reason) → ... → Done → Respond

Why it matters: Unlike a simple chatbot that gives a one-shot answer,
an agent using this loop can break complex tasks into steps, recover
from errors, adapt its plan based on real feedback, and use tools to
interact with the world.

For example, if you asked me to "find the top-performing lab and
summarize its stats," I'd go through multiple iterations of the loop:
list labs → pick one → fetch its data → analyze → format a response —
rather than guessing or giving a shallow answer.

Want me to demonstrate it with a real task?
```

**Query:** `uv run nanobot agent --logs --session cli:task1a-labs -c ./config.json -m "What labs are available in our LMS?"`

Before MCP was configured (Part A), the agent had no live LMS access. It inspected local repo files using built-in file tools and answered from documentation. After MCP was added, the same query now returns real backend data (see Task 1B below).

---

## Task 1B — Agent with LMS tools

**Query:** `uv run nanobot agent --logs --session cli:task1b-labs -c ./config.json -m "What labs are available?"`

**Agent response:**

```
Here are the available labs:

 ID      Title
 ───────────────────────────────────────────────────────────────
 lab-01  Lab 01 – Products, Architecture & Roles
 lab-02  Lab 02 — Run, Fix, and Deploy a Backend Service
 lab-03  Lab 03 — Backend API: Explore, Debug, Implement, Deploy
 lab-04  Lab 04 — Testing, Front-end, and AI Agents
 lab-05  Lab 05 — Data Pipeline and Analytics Dashboard
 lab-06  Lab 06 — Build Your Own Agent
 lab-07  Lab 07 — Build a Client with an AI Coding Agent
 lab-08  lab-08

There are 8 labs in total. Let me know if you'd like details on any
specific lab (pass rates, completion rates, top learners, group
performance, or submission timeline).
```

**Query:** `uv run nanobot agent --logs --session cli:task1b-health -c ./config.json -m "Is the LMS backend healthy?"`

**Agent response:**

```
Yes, the LMS backend is healthy! It currently has 56 items in the
system.
```

---

## Task 1C — Skill prompt

**Query:** `uv run nanobot agent --logs --session cli:task1c -c ./config.json -m "Show me the scores"`

**Agent response (key excerpts from the conversation log):**

```
I'll check the available labs first, then get the scores for you.
→ Tool call: mcp_lms_lms_labs({})

There are 8 labs available. Which one would you like to see scores for?
```

The LMS skill prompt successfully guided the agent to:
1. Call `lms_labs` first (as instructed in the skill: "if the user asks for scores without naming a lab, call `lms_labs` first")
2. Ask the user to choose a lab instead of guessing or returning data for a random lab

The skill teaches the strategy: when a lab-dependent query (scores, pass rates, completion, groups, timeline, top learners) arrives without a specific lab, the agent lists available labs and asks the user to pick one.

## Task 2A — Deployed agent

The nanobot gateway runs as a Docker Compose service. Startup logs:

```
nanobot-1  | Using config: /app/nanobot/config.resolved.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | MCP: registered tool 'mcp_lms_lms_health' from server 'lms'
nanobot-1  | MCP: registered tool 'mcp_lms_lms_labs' from server 'lms'
nanobot-1  | MCP: registered tool 'mcp_lms_lms_learners' from server 'lms'
nanobot-1  | MCP: registered tool 'mcp_lms_lms_pass_rates' from server 'lms'
nanobot-1  | MCP: registered tool 'mcp_lms_lms_timeline' from server 'lms'
nanobot-1  | MCP: registered tool 'mcp_lms_lms_groups' from server 'lms'
nanobot-1  | MCP: registered tool 'mcp_lms_lms_top_learners' from server 'lms'
nanobot-1  | MCP: registered tool 'mcp_lms_lms_completion_rate' from server 'lms'
nanobot-1  | MCP: registered tool 'mcp_lms_lms_sync_pipeline' from server 'lms'
nanobot-1  | MCP server 'lms': connected, 9 tools registered
nanobot-1  | Agent loop started
```

## Task 2B — Web client

**WebSocket test:** `echo '{"content":"How is the backend doing?"}' | websocat "ws://localhost:42002/ws/chat?access_key=1234567"`

**Agent response:**
```json
{"type":"text","content":"The LMS backend is **healthy** with **56 items** in the database. Everything looks good! 🟢","format":"markdown"}
```

**Structured UI test:** `echo '{"content":"Show me the scores"}' | websocat ...`

**Agent response (structured choice):**
```json
{
  "type":"choice",
  "content":"Which lab would you like to see scores for?",
  "options":[
    {"label":"Lab 01 – Products, Architecture & Roles","value":"lab-01"},
    {"label":"Lab 02 — Run, Fix, and Deploy a Backend Service","value":"lab-02"},
    {"label":"Lab 03 — Backend API: Explore, Debug, Implement, Deploy","value":"lab-03"},
    ...
  ]
}
```

The Flutter web client is accessible at `http://<vm-ip>:42002/flutter`.
The agent renders structured lab choices instead of raw JSON when the user asks an ambiguous question.

## Task 3A — Structured logging

**Happy-path structured log entries** from VictoriaLogs (JSON format):

```json
{"_time":"2026-04-03T19:41:28.693Z","severity":"INFO","service.name":"Learning Management Service","event":"request_started","trace_id":"0082cd4abcb6a100709f62fecbade46c","span_id":"e62c3c20f4972862"}
{"_time":"2026-04-03T19:41:28.694Z","severity":"INFO","service.name":"Learning Management Service","event":"auth_success","trace_id":"0082cd4abcb6a100709f62fecbade46c"}
{"_time":"2026-04-03T19:41:28.694Z","severity":"INFO","service.name":"Learning Management Service","event":"db_query","trace_id":"0082cd4abcb6a100709f62fecbade46c"}
{"_time":"2026-04-03T19:41:28.720Z","severity":"INFO","service.name":"Learning Management Service","event":"request_completed","trace_id":"0082cd4abcb6a100709f62fecbade46c"}
```

Each entry is structured JSON with `level` (severity), `service.name`, `event`, and `trace_id`.

**Error-path structured log entries** (postgres stopped):

```json
{"_time":"2026-04-03T19:42:14.466Z","severity":"ERROR","service.name":"Learning Management Service","event":"db_query","trace_id":"18b6a147608a2edb3dbfd3457488bc51","span_id":"6546ffb04bacfec5","error":"(sqlalchemy.dialects.postgresql.asyncpg.InterfaceError): connection is closed"}
{"_time":"2026-04-03T19:42:43.128Z","severity":"ERROR","service.name":"Learning Management Service","event":"db_query","trace_id":"2cb7214fab3a9ee7f69eee33a2abdd38","span_id":"3c43d3293b619cc2","error":"[Errno -2] Name or service not known"}
```

**VictoriaLogs UI query:** `_time:10m service.name:"Learning Management Service" severity:ERROR`
VictoriaLogs UI at `http://10.93.26.148:42002/utils/victorialogs/select/vmui` returns the above JSON entries with full structured fields.

---

## Task 3B — Traces

**Healthy trace screenshot:** At `http://10.93.26.148:42002/utils/victoriatraces` → trace `0082cd4a...` shows span hierarchy:
- `request_started` (0ms) → `auth_success` (1ms) → `db_query` (26ms) → `request_completed` (27ms)
- Total: ~40ms, no errors, all spans green

**Error trace screenshot:** Trace `18b6a147...` shows:
- `request_started` → `auth_success` → `db_query` (**ERROR**, 4,048ms, red span) → `request_completed`
- The `db_query` span has error tag: "connection is closed"

VictoriaTraces Jaeger API: `http://victoriatraces:10428/select/jaeger/api/traces/18b6a147608a2edb3dbfd3457488bc51`

---

## Task 3C — Observability MCP tools

Created `mcp/mcp-obs/` with 4 MCP tools:
- `mcp_obs_logs_search` — search VictoriaLogs with LogsQL queries
- `mcp_obs_logs_error_count` — count errors per service over a time window
- `mcp_obs_traces_list` — list recent traces for a service
- `mcp_obs_traces_get` — fetch a specific trace by ID

**Normal conditions** — "Any LMS backend errors in the last 10 minutes?":

Agent response:
```
Yes, there were 2 errors in the LMS backend in the last 10 minutes.
Both are related to database queries on the GET /items/ endpoint:

| Time     | Trace        | Issue                        |
|----------|-------------|------------------------------|
| 19:42:14 | 18b6a147... | SELECT query failed on db-lab-8 (692ms) |
| 19:42:43 | 2cb7214f... | Database connection failed — connect span timed out at 4,048ms |
```

**After postgres failure** — agent used `logs_error_count` → `logs_search` → extracted trace IDs → summarized:
```
The backend isn't looking great:
🔴 LMS Backend: Unhealthy — HTTP 404
📊 Recent Errors: 2 errors from Learning Management Service
- Both related to database queries on GET /items/
- Trace IDs: 18b6a147..., 2cb7214f...
```

## Task 4A — Multi-step investigation

**Agent response to "What went wrong?"** (with postgres stopped):

```
I've investigated the issue. Here's what I found:

**Affected Service:** Learning Management Service (LMS Backend)

**Log Evidence:**
- 19:42:14 — ERROR db_query: "sqlalchemy.dialects.postgresql.asyncpg.InterfaceError: connection is closed"
  trace_id: 18b6a147..., span_id: 6546ffb0...
- 19:42:43 — ERROR db_query: "[Errno -2] Name or service not known"
  trace_id: 2cb7214f..., span_id: 3c43d329...

**Trace Evidence:**
- Trace 18b6a147...: db_query span failed with 4,048ms timeout (ERROR tag)
- Trace 2cb7214f...: db_query span failed with connection error (ERROR tag)

**Root Cause:** The PostgreSQL database is unreachable. The db_query operation
is failing because the backend cannot connect to the database. The backend
returns HTTP 404 "Items not found" which misrepresents the actual database
connection failure as a missing resource.

**Summary:** PostgreSQL is down or unreachable. All LMS item queries fail with
database connection errors. The backend incorrectly returns 404 instead of 500.
```

The agent chained: `logs_error_count` → `logs_search` → `traces_get` → coherent summary citing both log and trace evidence.

---

## Task 4B — Proactive health check

Created cron job via Flutter chat: "Create a health check for this chat that runs every 2 minutes."

**Proactive health report** (while postgres still stopped):

```
📋 Health Check Report (last 2 minutes)

🔴 Unhealthy — 2 errors detected:
- Learning Management Service: 2 errors
- Both are db_query failures on GET /items/
- Root cause: PostgreSQL connection errors

The database is unreachable. All item listing requests return 404 instead of
the proper 500 error.
```

Agent used `cron({"action":"add",...})` to schedule, then `mcp_obs_logs_error_count({"minutes":2})` each cycle to check for fresh errors.

---

## Task 4C — Bug fix and recovery

**1. Root cause:** In `backend/src/lms_backend/routers/items.py` line 22-29, the `get_items()` endpoint had a broad `except Exception` that:
- Logged at WARNING level with event `items_list_failed_as_not_found`
- Returned HTTP 404 "Items not found" — misrepresenting a database failure as a missing resource
- Hid the actual error message from the user

**2. Fix:** Changed the exception handler to:
- Log at ERROR level with event `items_list_failed` and include `error` field
- Return HTTP 500 with the actual error detail: `"Failed to retrieve items: {exc}"`
- Use `HTTP_500_INTERNAL_SERVER_ERROR` instead of `HTTP_404_NOT_FOUND`

**Diff:**
```diff
-        logger.warning(
-            "items_list_failed_as_not_found",
-            extra={"event": "items_list_failed_as_not_found"},
-        )
+        logger.error(
+            "items_list_failed",
+            extra={"event": "items_list_failed", "error": str(exc)},
+        )
         raise HTTPException(
-            status_code=status.HTTP_404_NOT_FOUND,
-            detail="Items not found",
+            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
+            detail=f"Failed to retrieve items: {exc}",
         ) from exc
```

**3. Post-fix "What went wrong?"** (after redeploy, postgres still stopped):

```
The LMS backend is returning HTTP 500 errors on GET /items/:
- Error: "Failed to retrieve items: [Errno -2] Name or service not known"
- The backend now correctly reports the database connection failure as a 500
  instead of the previous misleading 404 "Items not found"
```

**4. Healthy follow-up** (after restarting postgres):

```
📋 Health Check Report (last 2 minutes)

✅ Healthy — No recent errors detected.
The LMS backend is responding normally. All services operational.
```
