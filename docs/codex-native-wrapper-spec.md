# Codex-Native Wrapper Spec

## Purpose

This document defines the first concrete backend for `multi-codex orchestration`.

The `codex-native wrapper` is a thin orchestration backend that stays inside the current Codex runtime and uses existing Codex agent tools rather than introducing a separate supervisor framework.

## Design Goal

The wrapper should provide enough structure for safe multi-role orchestration while preserving:
- current `tgtool` top-level routing
- current local skill behavior
- current Codex tool semantics
- current read-only and safety boundaries

## Tool Mapping

The first backend should map orchestration actions onto existing Codex tools.

| Wrapper action | Codex tool mapping |
|---|---|
| start orchestration session | local wrapper state + orchestration session id |
| spawn role | `spawn_agent` |
| send role task | `send_input` |
| wait for role result | `wait_agent` |
| stop role | `close_agent` |
| resume existing role if needed | `resume_agent` |

## Session Model

A codex-native orchestration session should contain:
- one orchestration session id
- one selected backend value: `codex-native`
- one role list
- one status per role
- one merged summary returned to `tgtool`

The wrapper does not replace the active `tgtool` session. It runs underneath it.

## Recommended Initial Flow

### Step 1: Normalize adapter input

The orchestration adapter should normalize input into:
- task summary
- role list
- constraints
- requested outcome
- optional write-scope map
- optional support layers

### Step 2: Spawn safe roles

The wrapper should spawn only the roles that are justified for the task.

Initial conservative rule:
- planner optional
- one implementer maximum
- one verifier maximum
- one reviewer maximum
- researcher only when clearly independent

### Step 3: Deliver role-specific instructions

Each role should receive:
- the shared task summary
- role-specific ownership
- constraints
- explicit write or read boundary
- expected output format

### Step 4: Collect and normalize results

The wrapper should wait for role completions and normalize them into:
- role status
- summary
- blockers
- artifacts
- fallback recommendation when needed

### Step 5: Return merged result to tgtool

The wrapper should return a backend-normalized result through the orchestration adapter rather than exposing backend-specific details directly to the user.

## Ownership and Safety Rules

The codex-native wrapper must preserve the same safety policy defined by `tgtool`.

It must:
- reject overlapping write scopes by default
- preserve strict read-only mode
- avoid spawning roles that cannot be given clear ownership
- prefer fewer roles over unsafe parallelism

## Fallback Conditions

The wrapper should return `fallback` instead of forcing orchestration when:
- `spawn_agent` is unavailable
- safe role decomposition is not possible
- strict read-only mode blocks meaningful execution
- the task is too small to justify orchestration
- role outputs cannot be normalized into a coherent result

## First-Release Constraints

The first implementation should stay deliberately small.

Recommended limits:
- one implementer only
- no overlapping write scopes
- no automatic nested orchestration
- no persistent background role pool
- no framework-specific memory layer beyond existing support layers

## Why This Backend Comes First

The codex-native wrapper is the best first backend because it:
- preserves the current local skill environment
- avoids introducing a second orchestration runtime too early
- keeps debugging and rollback simple
- gives `tgtool` a concrete orchestration path without committing to a heavy framework
