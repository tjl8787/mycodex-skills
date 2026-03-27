---
name: multi-codex-orchestration
description: Use when the user explicitly wants multiple Codex agents or a virtual team, the work can be decomposed into safe parallel roles, and tgtool should coordinate a codex-native orchestration path.
---

# Multi-Codex Orchestration

## Overview

Use this skill when a task should be executed by multiple Codex agents under a single routed session.

This skill does not replace `tgtool`. It provides the Phase 1 orchestration method that `tgtool` can route into.

Default backend:
- `codex-native wrapper`

Visible backend:
- `tmux-visible` when the user explicitly wants multiple foreground panes or windows

Phase 2 backend:
- `claude-flow` adapter when richer external orchestration is actually needed

Phase 2 helper assets included in this skill:
- `scripts/build_claude_flow_payload.py` to map a normalized session into a `claude-flow` backend payload
- `scripts/normalize_claude_flow_result.py` to map backend output back into the stable adapter result shape
- `templates/claude-flow-result-example.json` as a sample backend result for normalization

## When to Use

Use when all of these are true:
- the user explicitly wants multiple Codex agents, a virtual team, or parallel agent execution
- the task can be decomposed into 2+ relatively independent roles
- safe ownership boundaries can be defined
- sequential single-agent execution would be materially worse

Typical role set:
- `planner`
- `implementer`
- `verifier`
- `reviewer`
- optional `researcher`

## Do Not Use

Do not use when any of these are true:
- the task is tiny or obviously faster in one session
- write ownership would overlap in unsafe ways
- the work is pure read-only diagnosis without real parallel value
- strict read-only mode leaves no meaningful orchestration path
- the task is so coupled that role splitting would be artificial

## Phase 1 Backend

Helper assets included in this skill:
- `scripts/bootstrap_session.py` to create a wrapper session file
- `scripts/render_role_brief.py` to render a role-specific brief
- `scripts/ensure_ruflo_init.py` to detect or initialize `ruflo` Codex/runtime state
- `scripts/bootstrap_ruflo_backend.py` to automatically chain init and swarm bootstrap for `ruflo`
- `scripts/bootstrap_tmux_visible_backend.py` to open a visible tmux session with role panes
- `scripts/dispatch_tmux_role.py` to stream main-session stage instructions into visible role panes
- `scripts/broadcast_tmux_stage.py` to broadcast stage changes to all visible tmux role panes at once
- `templates/session-example.json` as a starter payload


Start with the `codex-native wrapper`.

Map orchestration actions to existing Codex tools:
- spawn roles with `spawn_agent`
- send role-specific work with `send_input`
- collect role results with `wait_agent`
- stop roles with `close_agent`
- resume a role with `resume_agent` if needed

Use the local backend first because it preserves current skills, current boundaries, and current Codex behavior.

## Supporting References

For Phase 1 and Phase 2 implementation details, also see:
- `docs/codex-native-wrapper-spec.md`
- `docs/codex-native-wrapper-session-schema.md`
- `docs/codex-native-wrapper-playbook.md`
- `docs/claude-flow-adapter-spec.md`
- `docs/claude-flow-adapter-playbook.md`
- `docs/ruflo-init-playbook.md`
- `docs/ruflo-runtime-bootstrap-playbook.md`
- `docs/tmux-visible-backend-playbook.md`
- `scripts/bootstrap_session.py`
- `scripts/render_role_brief.py`
- `scripts/ensure_ruflo_init.py`
- `scripts/bootstrap_ruflo_backend.py`
- `scripts/bootstrap_tmux_visible_backend.py`
- `scripts/dispatch_tmux_role.py`
- `scripts/broadcast_tmux_stage.py`
- `scripts/build_claude_flow_payload.py`
- `scripts/normalize_claude_flow_result.py`
- `templates/session-example.json`
- `templates/claude-flow-result-example.json`

## Process

### 1. Confirm orchestration eligibility

Before spawning any role, confirm:
- the task really benefits from parallel work
- the role split is meaningful
- write scopes can be kept disjoint
- the selected mode and safety boundaries still allow orchestration

If not, fall back instead of forcing orchestration.

### 2. Choose the smallest safe role set

Use the smallest role set that can safely move the task forward.

Conservative default:
- at most one `implementer`
- `planner` is read-heavy
- `verifier` owns validation, not main implementation
- `reviewer` is advisory and read-heavy
- add `researcher` only when discovery is clearly independent

### 3. Define ownership explicitly

For each role, state:
- what it owns
- what it must not edit
- what output it must return

Reject orchestration if ownership cannot be made clear enough.

### 4. Bootstrap the selected backend automatically

When the user explicitly wants a `ruflo` backend or asks to initialize orchestration runtime state:
- run `scripts/bootstrap_ruflo_backend.py` first
- let it ensure Codex integration if missing
- let it ensure runtime state if missing
- let it initialize a swarm through `ruflo swarm init --v3-mode`
- keep daemon startup optional instead of making it part of the default chain

When the user explicitly wants visible foreground workers, tmux panes, or front windows:
- run `scripts/bootstrap_tmux_visible_backend.py`
- create a named tmux session with one pane per role
- enable `tmux set-option -g mouse on`
- enable `tmux set-option -s set-clipboard on`
- keep the pane set conservative by default: `planner`, `implementer`, `verifier`, `reviewer`
- treat this backend as visibility-first, not as the default orchestration path
- keep a session state file so the main session can address roles deterministically
- use `scripts/dispatch_tmux_role.py` at each major stage so the user can watch role-specific work appear in the panes in real time
- use `scripts/broadcast_tmux_stage.py` when the main session changes stage and all visible panes should refresh together

### 5. Execute through the codex-native wrapper

Normalize the task into:
- task summary
- constraints
- requested outcome
- candidate roles
- optional support layers
- optional write-scope map

Then run the roles through the Codex tool mapping.

### 6. Normalize results

Collect per-role outputs into a stable result shape:
- orchestration session id
- backend used
- roles spawned
- per-role status
- blockers
- merged summary
- fallback recommendation if needed

Return the merged result back into the active `tgtool` session.

## Fallback Order

If orchestration should not continue, fall back in this order:
1. `subagent-driven-development`
2. `dispatching-parallel-agents`
3. ordinary `using-superpowers` routing
4. single-session execution

## Common Mistakes

- Spawning too many roles before ownership is clear
- Using two writing roles on the same files
- Treating `reviewer` as a hidden second implementer
- Forcing orchestration when the task is too small
- Treating the external framework as the top-level router instead of `tgtool`

## Remember

- `tgtool` stays the entrypoint
- Phase 1 uses the local `codex-native wrapper`
- visible terminal workers use the `tmux-visible` backend only when the user explicitly asks for foreground panes or windows
- explicit `ruflo` backend requests may first run `scripts/bootstrap_ruflo_backend.py` to initialize Codex/runtime state and a swarm automatically
- Phase 2 introduces `claude-flow`, but only behind the adapter
- prefer fewer roles over unsafe parallelism
