# Orchestration Backend Evaluation

## Purpose

This document compares the first three backend options for `multi-codex orchestration`.

The goal is to choose the smallest backend that preserves current `tgtool`, Codex, and local-skill behavior while still enabling safe multi-agent execution.

## Comparison Table

| Backend | What it is | Strengths | Weaknesses | Best use | Recommendation |
|---|---|---|---|---|---|
| Codex-native wrapper | A thin adapter that uses current Codex agent tools and local skills directly | Lowest integration cost, preserves current `tgtool` behavior, preserves local skills, easiest to debug, easiest to keep read-only boundaries | Limited by current runtime capabilities, may be less expressive for long-running swarms | First implementation, local multi-role orchestration, safe incremental rollout | **First choice** |
| tmux-based Codex orchestration | A wrapper that coordinates multiple Codex sessions through tmux or similar terminal multiplexing | Good terminal visibility, can model separate long-lived workers, closer to an external supervisor without leaving the Codex environment entirely | More process management overhead, more fragile session lifecycle, harder to normalize outputs cleanly | When Codex-native orchestration is not enough but terminal-native coordination still matters | **Second choice** |
| `claude-flow` backend adapter | An adapter that sends work to `ruvnet/claude-flow` as the first named external backend candidate | Richer swarm-style orchestration, stronger external role lifecycle, explicit named framework path | Highest integration cost, highest mismatch risk with current skills, more state and boundary complexity, weaker guarantee of preserving existing local behavior than local backends | Phase 2 only, or when external swarm behavior is explicitly needed | **Third choice** |

## Evaluation Criteria

The comparison is based on these priorities:
- preserve `tgtool` as the top-level route
- preserve current Codex local-skill behavior
- preserve clear read-only and safety boundaries
- minimize integration complexity and debugging cost
- allow future backend swaps without rewriting `tgtool`

## Recommended First Target

The first implementation target should be a **Codex-native wrapper**.

Reasons:
- it keeps the current Codex runtime and local skills as the primary execution environment
- it minimizes orchestration overhead for the first release
- it fits the current `tgtool -> orchestration adapter -> backend` boundary cleanly
- it leaves room to add tmux-based or `claude-flow` and other external-framework backends later without rewriting `tgtool`

## Escalation Path

Use this backend escalation order:
1. Codex-native wrapper
2. tmux-based Codex orchestration
3. `claude-flow` backend adapter

Move to the next layer only when the lower layer cannot safely provide the needed role lifecycle, concurrency, or visibility.

## Non-Goal

The first backend choice does not commit the system to a permanent framework.

It only defines the preferred starting point for the adapter implementation.
