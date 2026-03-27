# Tmux-Visible Backend Playbook

## Purpose

Use this playbook when the user explicitly wants to see multiple foreground workers in separate panes or windows instead of relying on background-only orchestration.

This backend is visibility-first. It does not replace the default `codex-native wrapper`. It exists for users who want a live terminal view of role separation.

## Trigger Conditions

Use this backend only when the user explicitly asks for any of:
- visible workers
- foreground panes
- front windows
- tmux-based multi-agent execution

Do not choose it silently as the default backend.

## Default Pane Set

Start with one tmux session and four panes:
- `planner`
- `implementer`
- `verifier`
- `reviewer`

Keep the first version conservative. Do not create additional panes unless the user clearly asks for a broader role set.

## Bootstrap Behavior

Use `skills/multi-codex-orchestration/scripts/bootstrap_tmux_visible_backend.py` to:
- create or reuse a named tmux session
- split panes into the default role layout
- label each pane with a role banner
- prefer `shell` pane mode by default so each visible pane stays controllable and can execute real shell commands or one-shot `codex 'prompt'` runs
- use `codex` pane mode only when the user explicitly wants long-lived interactive Codex panes
- write a session state file with stable role-to-pane targets
- print the attach command

Use `scripts/execute_tmux_role_command.py` when a role pane should visibly run a real shell command.

Use `scripts/run_tmux_role_codex.py` when a role pane should visibly run a one-shot Codex task through the shell.

Use `skills/multi-codex-orchestration/scripts/dispatch_tmux_role.py` whenever the main session changes stage or hands work to a role:
- planner gets planning-stage guidance
- implementer gets implementation-stage guidance
- verifier gets verification-stage guidance
- reviewer gets review-stage guidance

This keeps the visible panes aligned with what the main session is doing instead of leaving them as detached shells.

Use `skills/multi-codex-orchestration/scripts/broadcast_tmux_stage.py` when the main session changes stage and all panes should visibly update together.

The intended pattern is:
- stage change -> `broadcast_tmux_stage.py`
- role-specific handoff -> `dispatch_tmux_role.py`

## Output Contract

Return:
- backend used: `tmux-visible`
- tmux session name
- role list
- attach command
- whether the session was newly created or reused
- session state file path

## Safety Rules

- do not use this backend in strict read-only mode if the user only wants passive diagnosis and the tmux session would add no real value
- do not silently create overlapping writer panes
- prefer one `implementer` pane unless the user explicitly wants broader write parallelism and ownership is safe
