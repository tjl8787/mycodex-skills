# Ruflo Execution Playbook

Use this playbook when `tgtool` routes into `multi-codex orchestration`, the user explicitly wants the `ruflo` backend, and the task should move beyond bootstrap into real multi-agent execution.

## Rule of Thumb

- `ruflo` CLI is the bootstrap layer.
- `claude_flow` MCP tools are the live execution layer inside the current Codex session.
- A shell-side probe can validate the local CLI path, but it is not the main execution path.

## Recommended Execution Chain

1. Bootstrap local runtime state:
   - `skills/multi-codex-orchestration/scripts/bootstrap_ruflo_backend.py`
2. Use the current session's `claude_flow` tool family to execute real orchestration:
   - initialize swarm
   - spawn role agents
   - create tasks
   - assign tasks
   - monitor task, agent, and swarm status
3. Summarize status back into the active `tgtool` session.

## Why This Split Exists

Shell-side `ruflo` commands are useful, but they do not fully drive in-session execution on their own.

Observed behavior:
- `ruflo swarm start ...` can initialize agent slots and topology
- `ruflo hive-mind spawn --claude ...` prepares a Claude-oriented execution prompt
- `ruflo` CLI task/agent primitives can create IDs and assignments

But for the current Codex environment, the most reliable way to drive actual multi-agent execution is:
- bootstrap with `ruflo`
- execute with the `claude_flow` orchestration tools already exposed in-session

## Minimal In-Session Execution Pattern

Use this order:
- swarm init
- agent spawn
- task create
- task assign
- task status / agent status / swarm status

Keep the role set conservative:
- `operator` for concrete execution
- keep `critic` dormant by default
- wake `critic` only on failure, stage transition, or explicit review/feedback demand
- wake extra roles only when the task truly needs them

## Shell-Side Probe

When you need a quick executable sanity check for the local `ruflo` CLI path, run:

```bash
python3 skills/multi-codex-orchestration/scripts/probe_ruflo_execution.py --project-dir .
```

That probe should verify that the local `ruflo` CLI can:
- create or bootstrap runtime state
- create a swarm
- spawn an agent
- create a task
- assign the task

Do not treat the probe as proof that long-running in-session worker execution is already wired.
