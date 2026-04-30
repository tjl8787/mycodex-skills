# Skill Temporary Toggle

This helper script gives a practical "temporary enable" workflow for skills that are disabled in `~/.codex/config*.toml`.

- Enable disabled skills for the current task.
- Track only skills that were previously `enabled = false`.
- Reset those tracked skills back to `false` after task completion.
- Skills already enabled by default are untouched by `reset`.

## Commands

```bash
python3 tools/skill_temp_toggle.py on <skill1> [skill2 ...]
python3 tools/skill_temp_toggle.py status
python3 tools/skill_temp_toggle.py reset
```

Examples:

```bash
python3 tools/skill_temp_toggle.py on systematic-debugging test-driven-development
python3 tools/skill_temp_toggle.py reset
```

## Options

- `--config <path>`: override target config file (can pass multiple times)
- `--state-file <path>`: override state JSON path

## Notes

- Default config targets:
  - `~/.codex/config.toml`
  - `~/.codex/config.chatgpt.toml`
- Default state file:
  - `~/.codex/skill-temp-state.json`
- If you see write-permission errors, run in an environment where these files are writable.
