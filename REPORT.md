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

**Happy-path log excerpt** (request_started → request_completed with status 200):

```
backend-1  | 2026-04-03 19:41:28,693 INFO [lms_backend.main] - request_started
backend-1  | 2026-04-03 19:41:28,694 INFO [lms_backend.auth] - auth_success
backend-1  | 2026-04-03 19:41:28,694 INFO [lms_backend.db.items] - db_query
backend-1  | 2026-04-03 19:41:28,720 INFO [lms_backend.main] - request_completed
backend-1  | INFO:     172.18.0.9:52534 - "GET /items/ HTTP/1.1" 200 OK
```

Each line includes structured fields: `trace_id`, `span_id`, `service.name`, and `event`.

**Error-path log excerpt** (db_query with error, postgres stopped):

```
backend-1  | 2026-04-03 19:42:14,466 ERROR [lms_backend.db.items] - db_query
backend-1  | 2026-04-03 19:42:14,478 WARNING [lms_backend.routers.items] - items_list_failed_as_not_found
backend-1  | INFO:     172.18.0.9:47942 - "GET /items/ HTTP/1.1" 404 Not Found
```

The ERROR entry contains: `trace_id=18b6a147608a2edb...`, `event=db_query`, full SQLAlchemy error message.

**VictoriaLogs query:** `_time:10m service.name:"Learning Management Service" severity:ERROR`

Returned 2 error entries with full structured JSON including `trace_id`, `error`, `span_id`, `event`.

Query via HTTP API: `curl "http://localhost:42010/select/logsql/query?query=_time:10m%20service.name:%22Learning%20Management%20Service%22%20severity:ERROR"`

---

## Task 3B — Traces

**Healthy trace:** The trace for a successful `GET /items/` request shows spans:
- `request_started` → `auth_success` → `db_query` → `request_completed`
- All spans completed in ~40ms with no errors
- Trace ID: `0082cd4abcb6a100709f62fecbade46c`

**Error trace:** When postgres was stopped, the trace shows:
- `request_started` → `auth_success` → `db_query` (**ERROR**, 4,048ms timeout) → `request_completed` (404)
- The `db_query` span has an error tag with "connection is closed"
- Trace ID: `18b6a147608a2edb3dbfd3457488bc51`

Traces can be found via VictoriaTraces Jaeger API:
- `http://victoriatraces:10428/select/jaeger/api/traces?service=Learning%20Management%20Service&limit=10`
- `http://victoriatraces:10428/select/jaeger/api/traces/<traceID>`

---

## Task 3C — Observability MCP tools

Created `mcp/mcp-obs/` with 4 MCP tools:
- `mcp_obs_logs_search` — search VictoriaLogs with LogsQL queries
- `mcp_obs_logs_error_count` — count errors per service over a time window
- `mcp_obs_traces_list` — list recent traces for a service
- `mcp_obs_traces_get` — fetch a specific trace by ID

**Normal conditions** — "Any LMS backend errors in the last 10 minutes?":

The agent reported 2 errors from the earlier postgres failure with trace IDs and timestamps, showing it can query VictoriaLogs and extract trace IDs.

**After postgres failure** — same question immediately after stopping postgres:

```
The backend isn't looking great. Here's the current status:

**🔴 LMS Backend: Unhealthy**
- Health check returning HTTP 404
- Item count unknown

**📊 Recent Errors (last 30 minutes)**
- 2 errors from Learning Management Service
- Both related to database queries on GET /items/
- Trace IDs: 18b6a147..., 2cb7214f...
```

The agent used `logs_error_count` → `logs_search` → extracted trace IDs → summarized findings concisely.

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
