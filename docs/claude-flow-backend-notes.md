# Claude-Flow Backend Notes

## Purpose

This document defines how `ruvnet/claude-flow` fits into `multi-codex orchestration` as the first named external backend candidate.

It does not replace `tgtool`. It sits behind the orchestration adapter.

## Architecture Position

The routing remains:
- `tgtool`
- `orchestration adapter`
- backend

When selected, `claude-flow` occupies the backend slot only.

## Why It Is Phase 2

`claude-flow` is introduced after the `codex-native wrapper` because:
- the local wrapper is the smaller first implementation
- it preserves current Codex behavior more directly
- `claude-flow` adds more orchestration power, but also more integration cost

## When to Prefer Claude-Flow

Prefer `claude-flow` when:
- richer swarm-style orchestration is actually needed
- the task needs a stronger external role lifecycle than the local wrapper provides
- the user explicitly wants the external framework path
- the orchestration value justifies the added integration overhead

## Adapter Requirement

If `claude-flow` is used, the orchestration adapter must still normalize:
- input payload
- role model
- session id
- role status summaries
- blockers
- merged result
- fallback reason

`tgtool` should not need direct framework-specific knowledge.
