# Codex-Native Wrapper Session Schema

## Purpose

This document defines the minimal session state for the Phase 1 `codex-native wrapper`.

The goal is to keep orchestration state small, explicit, and easy to debug.

## Required Fields

| Field | Type | Description |
|---|---|---|
| `orchestration_session_id` | string | Stable id for the wrapper session |
| `backend` | string | Must be `codex-native` for Phase 1 |
| `workspace_path` | string | Absolute repo or project path |
| `task_summary` | string | Compact summary of the routed work |
| `requested_outcome` | string | What completion means for this run |
| `constraints` | array[string] | Shared constraints inherited from `tgtool` |
| `roles` | array[object] | Declared role set with ownership and status |
| `status` | string | Session status: `running`, `complete`, `fallback`, `blocked`, `failed` |
| `summary` | string | Current merged session summary |

## Role Object

Each role entry should include:

| Field | Type | Description |
|---|---|---|
| `role` | string | Role name such as `planner`, `implementer`, `verifier`, `reviewer` |
| `agent_id` | string | Spawned Codex agent id |
| `status` | string | Current role status |
| `ownership` | string | High-level ownership summary |
| `write_scope` | array[string] | Allowed write targets, if any |
| `last_summary` | string | Latest normalized role update |

## Optional Fields

| Field | Type | Description |
|---|---|---|
| `support_layers` | array[string] | Active support layers such as `planning-with-files` |
| `evidence_snapshot` | string | Shared verified context used at session start |
| `blockers` | array[string] | Active blockers |
| `artifacts` | array[string] | Relevant files or outputs |
| `fallback_reason` | string | Reason for leaving orchestration |
| `handoff_recommendation` | string | Suggested next route after fallback |

## Example Session

```json
{
  "orchestration_session_id": "orch-20260327-001",
  "backend": "codex-native",
  "workspace_path": "/data/myproject/bucketmanager",
  "task_summary": "Implement feature X with parallel verification",
  "requested_outcome": "code change plus verification summary",
  "constraints": [
    "keep tgtool as top-level session",
    "no remote changes"
  ],
  "roles": [
    {
      "role": "implementer",
      "agent_id": "agent-impl-1",
      "status": "running",
      "ownership": "main production change",
      "write_scope": ["src/feature_x.py"],
      "last_summary": "Preparing patch"
    },
    {
      "role": "verifier",
      "agent_id": "agent-ver-1",
      "status": "running",
      "ownership": "focused validation",
      "write_scope": ["tests/test_feature_x.py"],
      "last_summary": "Building verification plan"
    }
  ],
  "status": "running",
  "summary": "Implementation and verification are in progress"
}
```

## State Discipline

The wrapper should prefer:
- one authoritative session record
- compact summaries over raw logs
- normalized role state over backend-specific details

The session schema is not a long-term memory layer. It is only the active orchestration state for the current run.
