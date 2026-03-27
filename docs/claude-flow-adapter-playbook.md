# Claude-Flow Adapter Playbook

## Purpose

This playbook defines the operational steps for a Phase 2 `claude-flow` adapter run.

## Phase 2 Default Sequence

### 1. Confirm escalation from Phase 1

Before using `claude-flow`, confirm that at least one of these is true:
- richer external orchestration is actually needed
- the local wrapper is insufficient
- the user explicitly wants the external backend

If not, stay on Phase 1.

### 2. Normalize the session

Start from the same normalized orchestration input used by the generic adapter:
- task summary
- requested outcome
- constraints
- candidate roles
- optional support layers
- optional write-scope map

### 3. Build a backend payload

Translate the normalized payload into a `claude-flow` backend payload.

The payload should preserve:
- orchestration session id
- role model
- ownership boundaries
- fallback expectations

### 4. Execute the backend path

Run the external backend through the adapter boundary.

Do not let framework-specific concepts replace:
- the stable session id
- the stable result shape
- the stable fallback behavior

### 5. Normalize backend results

Convert backend-specific output into the stable orchestration adapter output shape.

The normalized output should answer:
- what backend ran
- which roles were actually used
- whether the run completed, blocked, failed, or should fall back
- what summary the active `tgtool` session should report

## Heuristics

Use these heuristics:
- keep `claude-flow` as an explicit Phase 2 escalation, not the default
- preserve the same role boundaries defined for local orchestration
- prefer returning a normalized fallback over leaking raw backend complexity into the session

## Exit Conditions

Exit back to ordinary orchestration routing when:
- the backend is unavailable
- the backend produces unusable or ambiguous state
- the external backend no longer adds enough value over the local wrapper
