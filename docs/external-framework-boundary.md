# External Framework Boundary

## Purpose

This document defines the boundary between `tgtool`, the orchestration adapter, and any external multi-agent framework.

The intent is to preserve `tgtool` as the top-level route while allowing orchestration backends to evolve independently.

## Ownership Split

### tgtool owns

`tgtool` remains responsible for:
- mode selection
- global rules and visibility
- strict read-only enforcement
- shared-environment and safety boundaries
- support-layer selection such as `planning-with-files` or `claude-mem`
- deciding whether a task should enter `multi-codex orchestration`
- concise user-facing routing explanations

### orchestration adapter owns

The adapter is responsible for:
- normalizing routed work into an orchestration-friendly payload
- backend selection and invocation
- role spawning and session setup
- role status collection and normalization
- fallback signaling when orchestration should stop
- returning a merged status/result back into the active tgtool session

### external framework owns

The external framework, if used, is responsible for:
- backend-specific task decomposition
- backend-specific role lifecycle
- backend-specific task dispatch
- backend-specific message passing or memory coordination
- backend-specific execution details

## Framework-Agnostic Requirement

The adapter boundary must remain framework-agnostic.

`tgtool` should not need structural changes if the backend later changes between:
- a Codex-native wrapper
- a tmux-based Codex orchestrator
- an external framework such as a swarm or harness system

Only the adapter contract and backend implementation should vary.

## Entry and Exit Rules

### Entry into orchestration

A task may enter `multi-codex orchestration` only when:
- the user explicitly wants multiple Codex agents or a virtual team
- the task can be decomposed into relatively independent roles
- ownership can be made safe enough for parallel execution

### Exit from orchestration

Control should return to ordinary `tgtool` routing when:
- the backend is unavailable
- decomposition is rejected
- role ownership is ambiguous
- strict read-only mode blocks meaningful orchestration
- the orchestration overhead exceeds the task value

## Non-Goals

This boundary does not make the external framework the primary user-facing system.

It does not:
- replace `tgtool` as the entrypoint
- replace ordinary superpowers routing for common development work
- force every multi-step task through orchestration
- assume a specific framework is permanently chosen

## Recommended First Backend Strategy

For the initial implementation, prefer the smallest backend that preserves current Codex behavior and local skills.

That means prioritizing:
1. Codex-native orchestration or wrapper logic
2. tmux-style Codex orchestration if necessary
3. larger external frameworks only when the lighter paths are insufficient
