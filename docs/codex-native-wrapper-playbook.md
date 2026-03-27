# Codex-Native Wrapper Playbook

## Purpose

This playbook defines the operational steps for a Phase 1 `codex-native wrapper` run.

It is the execution-facing companion to the wrapper spec and session schema.

## Phase 1 Default Sequence

### 1. Start session

Create a new orchestration session with:
- session id
- normalized task summary
- requested outcome
- shared constraints
- initial role list

### 2. Validate role safety

Before spawning roles, check:
- is the role split meaningful?
- are write scopes disjoint enough?
- does strict read-only mode block the write path?
- is orchestration worth the overhead?

If not, return `fallback` immediately.

### 3. Spawn roles

Use the smallest safe role set.

Default conservative pattern:
- optional `planner`
- one `implementer`
- one `verifier`
- one `reviewer`
- optional `researcher`

### 4. Deliver role prompts

Each role prompt should include:
- shared task summary
- role-specific goal
- ownership boundary
- forbidden areas
- expected output format

### 5. Collect updates

Use role updates to refresh:
- per-role status
- blockers
- artifacts
- merged summary

Do not expose raw orchestration internals unless they materially affect user decisions.

### 6. Merge result

When the run completes, return:
- backend used
- roles spawned
- per-role status summary
- final merged summary
- blockers or fallback reason if relevant

## Wrapper Heuristics

Use these heuristics by default:
- fewer roles are better than unsafe role inflation
- one implementer is safer than multiple writers
- reviewer should not silently become the implementer
- verifier should validate rather than absorb feature work
- fallback is better than brittle orchestration

## First-Release Constraints

The first working wrapper should avoid:
- nested orchestration
- background worker pools
- overlapping write ownership
- framework-specific memory layers
- automatic escalation to external frameworks

## Exit Conditions

Exit to ordinary routing when:
- ownership becomes ambiguous
- role updates cannot be normalized cleanly
- orchestration overhead becomes larger than the task value
- the local wrapper cannot safely continue

Recommended fallback order:
1. `subagent-driven-development`
2. `dispatching-parallel-agents`
3. ordinary `using-superpowers`
4. single-session execution
