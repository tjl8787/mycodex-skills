# Orchestration Adapter Contract

## Purpose

The orchestration adapter is the compatibility layer between `tgtool` and any multi-agent execution backend.

`tgtool` remains the top-level router. The adapter translates routed work into a backend-specific orchestration session and normalizes outputs back into the active `tgtool` session.

## Responsibilities

The adapter owns:
- task normalization for orchestration-eligible work
- backend session startup and teardown
- role-to-task assignment handoff
- execution status aggregation
- backend result normalization
- fallback signaling when orchestration should not continue

The adapter does **not** own:
- tgtool mode selection
- global safety boundaries
- read-only enforcement
- support-layer selection policy
- final user-facing routing policy

## Input Contract

The adapter input should be represented as a structured payload with these fields.

### Required fields

| Field | Type | Description |
|------|------|-------------|
| `task_summary` | string | Compact summary of the user request |
| `mode` | string | Current `tgtool` mode: `review`, `standard`, or `autopilot` |
| `workspace_path` | string | Absolute path to the working repository or project |
| `constraints` | array[string] | Confirmed constraints that all roles must honor |
| `requested_outcome` | string | What counts as completion for this orchestration session |
| `candidate_roles` | array[string] | Proposed role split such as `planner`, `implementer`, `verifier`, `reviewer` |

### Optional fields

| Field | Type | Description |
|------|------|-------------|
| `support_layers` | array[string] | Enabled support layers such as `planning-with-files` or `claude-mem` |
| `evidence_snapshot` | string | Compact verified context to avoid redundant rediscovery |
| `preferred_backend` | string | Optional backend preference such as `codex-native`, `tmux-wrapper`, or external framework name |
| `write_scope_map` | object | Optional mapping from role to allowed files/modules |
| `timeout_hint` | string | Optional expected duration hint |
| `read_only` | boolean | Whether strict read-only restrictions are active |

## Example Input

```json
{
  "task_summary": "Implement feature X and validate it with parallel verification",
  "mode": "autopilot",
  "workspace_path": "/data/myproject/bucketmanager",
  "constraints": [
    "do not touch remote environments",
    "preserve current tgtool session visibility"
  ],
  "requested_outcome": "merged local implementation result plus verification summary",
  "candidate_roles": ["planner", "implementer", "verifier", "reviewer"],
  "support_layers": ["planning-with-files"],
  "evidence_snapshot": "Current repo state is clean; feature scope is limited to local files.",
  "preferred_backend": "codex-native",
  "read_only": false
}
```

## Output Contract

The adapter output should always normalize backend-specific results into a stable shape.

### Required fields

| Field | Type | Description |
|------|------|-------------|
| `orchestration_session_id` | string | Stable id for the orchestration run |
| `backend` | string | Backend actually used |
| `roles_spawned` | array[string] | Roles actually created |
| `status` | string | One of `running`, `complete`, `fallback`, `blocked`, `failed` |
| `role_statuses` | array[object] | Per-role status summary |
| `summary` | string | Compact merged summary of current or final result |

### Optional fields

| Field | Type | Description |
|------|------|-------------|
| `artifacts` | array[string] | Relevant files, patches, docs, or outputs |
| `blockers` | array[string] | Remaining blockers if not complete |
| `fallback_reason` | string | Why the adapter declined or exited to fallback |
| `handoff_recommendation` | string | Suggested next workflow if orchestration stops |

## Example Output

```json
{
  "orchestration_session_id": "orch-20260327-001",
  "backend": "codex-native",
  "roles_spawned": ["planner", "implementer", "verifier", "reviewer"],
  "status": "complete",
  "role_statuses": [
    {"role": "planner", "status": "complete", "summary": "Task split accepted"},
    {"role": "implementer", "status": "complete", "summary": "Code changes prepared"},
    {"role": "verifier", "status": "complete", "summary": "Focused validation passed"},
    {"role": "reviewer", "status": "complete", "summary": "No blocking review findings"}
  ],
  "summary": "Implementation and verification completed with no blocking review issues.",
  "artifacts": [
    "src/feature_x.py",
    "tests/test_feature_x.py"
  ]
}
```

## Failure and Fallback States

The adapter must return a normalized fallback result instead of silently failing.

### `fallback`
Use when orchestration should stop and control should return to ordinary `tgtool` routing.

Common reasons:
- backend unavailable
- decomposition rejected
- conflicting write scopes across roles
- strict read-only mode blocks meaningful orchestration
- task is too small to justify orchestration overhead

### `blocked`
Use when orchestration is conceptually valid but cannot proceed until something external changes.

Examples:
- missing credentials
- missing backend runtime
- missing workspace access

### `failed`
Use only when the adapter itself or the backend execution path failed unexpectedly and did not produce a trustworthy result.

## Fallback Recommendations

When returning `fallback`, the adapter should suggest a safe next route:
- `subagent-driven-development`
- `dispatching-parallel-agents`
- ordinary `using-superpowers`
- single-session execution

## Contract Rule

The adapter contract should stay framework-agnostic.

`tgtool` should not be forced to change if the backend later changes from:
- a Codex-native wrapper
- a tmux-based Codex orchestrator
- an external orchestration framework

Only the adapter implementation should change.
