# Claude-Flow Adapter Spec

## Purpose

This document defines the Phase 2 adapter path for `ruvnet/claude-flow`.

The `claude-flow` adapter remains behind `tgtool` and the orchestration adapter. It does not become the user-facing entrypoint.

## Design Goal

The adapter should preserve the same top-level behavior as Phase 1 while allowing an external swarm-style backend when the local wrapper is not sufficient.

## Adapter Responsibilities

The `claude-flow` adapter should:
- transform the normalized orchestration payload into a `claude-flow`-friendly backend payload
- preserve the selected role model from `multi-codex-orchestration`
- keep `tgtool` safety and read-only boundaries intact
- normalize backend results back into the stable orchestration adapter contract

The adapter should not:
- replace `tgtool` routing
- bypass safety boundaries
- expose framework-specific details as the primary user-facing status model

## Expected Backend Payload

A Phase 2 backend payload should contain at least:
- backend name: `claude-flow`
- orchestration session id
- task summary
- requested outcome
- constraints
- candidate roles
- optional write-scope map
- optional support layers
- optional evidence snapshot

## Result Normalization

The adapter must normalize `claude-flow` output back into:
- `orchestration_session_id`
- `backend`
- `roles_spawned`
- `status`
- `role_statuses`
- `summary`
- optional `artifacts`
- optional `blockers`
- optional `fallback_reason`
- optional `handoff_recommendation`

## Use Threshold

The adapter should be preferred only when at least one of these is true:
- the task clearly benefits from richer swarm-style coordination
- the local wrapper cannot provide enough orchestration visibility
- the local wrapper cannot model the needed role lifecycle cleanly
- the user explicitly prefers `claude-flow`

## Fallback Rule

If `claude-flow` is unavailable, incomplete, or produces untrustworthy backend state, return control to the Phase 1 backend or the ordinary fallback chain instead of forcing the external backend path.
