# Orchestration Role Model

## Purpose

This document defines the default role model for `multi-codex orchestration`.

The goal is to maximize safe parallelism without creating write conflicts, duplicated work, or unclear ownership.

## Default Role Set

The first implementation should use four default roles.

| Role | Primary responsibility | Default write ownership |
|------|------------------------|-------------------------|
| `planner` | Task decomposition and execution sequencing | No production-code ownership |
| `implementer` | Main code changes | Explicit write scope only |
| `verifier` | Focused validation and test execution | No main implementation ownership |
| `reviewer` | Merge-quality review and conflict detection | No main implementation ownership |

## Optional Role

| Role | Use when | Default write ownership |
|------|----------|-------------------------|
| `researcher` | External or repo-level discovery is substantial and independent | No production-code ownership by default |

## Ownership Rules

### Planner

The planner:
- may inspect code, docs, tests, and repo structure
- may propose file ownership and task splits
- should not own production code edits as its primary output
- should not become a disguised implementer

### Implementer

The implementer:
- owns the primary write scope
- should receive explicit file or module responsibility
- should not review its own work as the final authority
- should not modify files outside the agreed ownership boundary unless escalated back to the orchestrator

### Verifier

The verifier:
- owns validation work that does not overlap with the implementer's primary write scope
- should prefer tests, focused checks, repros, and evidence collection
- may add minimal verification-only artifacts when necessary
- should not become a second implementer

### Reviewer

The reviewer:
- owns quality review, merge-readiness review, and conflict detection
- should focus on bugs, regressions, boundary violations, and missing verification
- should not own the main implementation write scope
- may suggest follow-up changes, but should not silently absorb implementation ownership

### Researcher

The researcher:
- is useful when discovery can run in parallel with implementation
- should focus on documentation, external references, or codebase reconnaissance
- should not own the main code path by default

## Write-Scope Rules

Parallel roles are only safe when ownership is clear.

The orchestrator should:
- assign an explicit write scope to each writing role
- avoid overlapping write scopes unless the overlap is intentionally serialized
- reject orchestration when safe ownership cannot be made clear enough

Examples of acceptable write splits:
- implementer owns `src/...`
- verifier owns `tests/...`
- reviewer is read-only

Examples of unsafe splits:
- two implementers editing the same service file without serialization
- verifier and implementer both editing the same production module simultaneously
- planner editing production code while also owning decomposition

## Review Boundary

The reviewer is advisory but important.

Its job is to answer:
- Is the work coherent?
- Are there correctness risks?
- Is ownership boundary respected?
- Is verification sufficient?

The reviewer should not become a hidden final implementer.

## Escalation Rules

Return control to the orchestrator when:
- ownership becomes ambiguous
- two roles need the same write scope at the same time
- verification requires behavioral changes rather than validation
- the original decomposition turns out to be wrong

## Suggested First-Release Policy

For the initial release of `multi-codex orchestration`:
- use one `implementer` only
- keep `planner` and `reviewer` read-heavy
- let `verifier` own validation work, not main implementation
- add `researcher` only when the task clearly benefits from parallel discovery

This keeps the first version conservative, easier to reason about, and less likely to create agent contention.
