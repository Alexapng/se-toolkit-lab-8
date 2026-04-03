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

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
