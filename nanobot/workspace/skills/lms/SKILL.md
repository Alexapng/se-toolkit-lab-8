---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

This skill teaches the agent how to use LMS MCP tools effectively to answer questions about labs, learners, and performance data.

## Available Tools

The following `lms_*` tools are available via the LMS MCP server:

- **lms_health**: Check if the LMS backend is healthy. Returns item count. No parameters needed.
- **lms_labs**: List all labs available in the LMS. Returns lab IDs and titles. No parameters needed.
- **lms_learners**: List all learners registered in the LMS. No parameters needed.
- **lms_pass_rates**: Get pass rates (average score and attempt count per task) for a specific lab. Requires `lab` parameter.
- **lms_timeline**: Get submission timeline (date + submission count) for a lab. Requires `lab` parameter.
- **lms_groups**: Get group performance (average score + student count per group) for a lab. Requires `lab` parameter.
- **lms_top_learners**: Get top learners by average score for a lab. Requires `lab` and optional `limit` (default 5) parameters.
- **lms_completion_rate**: Get completion rate (passed / total) for a lab. Requires `lab` parameter.
- **lms_sync_pipeline**: Trigger the LMS sync pipeline to import fresh data. Use when labs show 0 records.

## Strategy

### When the user asks for lab data without specifying a lab

If the user asks for scores, pass rates, completion, groups, timeline, or top learners **without naming a lab**:

1. Call `lms_labs` first to get available labs
2. If only one lab exists, use it directly
3. If multiple labs are available, ask the user to choose one
   - Use the lab titles from `lms_labs` as the choice labels
   - Use the lab IDs (e.g., `lab-04`) as the choice values
   - Let the shared `structured-ui` skill decide how to present that choice on supported channels

### When the user asks "what can you do?"

Explain your current tools and limits clearly:
- You can query live LMS data: lab lists, health, pass rates, completion rates, group performance, top learners, submission timelines
- You can trigger the sync pipeline to refresh data
- You do NOT have access to individual student grades or submission details beyond what the tools expose

### Formatting results

- Format numeric results clearly: percentages with `%` symbol, counts as numbers
- Use tables or bullet lists for structured data
- Keep responses concise — don't dump raw JSON
- Round percentages to 1 decimal place (e.g., `75.3%`)

### When labs show 0 records

If `lms_labs` returns labs but they show 0 items or 0 data:
- Call `lms_health` to check backend status
- If health shows low item count, call `lms_sync_pipeline` to trigger data import
- Then retry the original query

### General principles

- Always call `lms_labs` first when lab context is needed
- Use each lab title as the default user-facing label unless the tool output gives a better identifier
- Keep responses concise and focused on what the user asked for
- Don't call tools that weren't requested (e.g., don't fetch pass rates when asked for completion rate)
