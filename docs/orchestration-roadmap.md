# Multi-Codex Orchestration Roadmap

## Phase 1

**Backend:** `codex-native wrapper`

Phase 1 focuses on the smallest viable orchestration backend that preserves the current Codex runtime and local skill behavior.

Goals:
- keep `tgtool` as the top-level entrypoint
- keep orchestration inside the current Codex runtime
- map orchestration onto existing Codex agent tools
- keep ownership conservative and debugging simple

## Phase 2

**Backend:** `claude-flow` adapter

Phase 2 introduces `ruvnet/claude-flow` as the first named external backend for `multi-codex orchestration`.

Goals:
- preserve the same `tgtool -> orchestration adapter -> backend` boundary
- allow richer external swarm-style orchestration when Phase 1 is insufficient
- keep `tgtool` and the adapter framework-agnostic even while adding a named external backend

## Transition Rule

Move from Phase 1 to Phase 2 only when one or more of these become true:
- the local wrapper cannot provide the needed role lifecycle
- the local wrapper cannot provide enough orchestration visibility
- the task benefits materially from an external swarm-style backend
- the user explicitly wants the `claude-flow` path

## Stability Rule

Phase 1 remains the default until the `claude-flow` path is documented and justified.
