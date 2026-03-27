# Ruflo Init Playbook

Use this playbook when `tgtool` routes into `multi-codex orchestration` and the user explicitly wants a `ruflo` backend or asks to initialize the orchestration runtime.

## Targets

- `codex`
  - Creates Codex-facing integration files such as `AGENTS.md` and `.agents/config.toml`
  - Command: `ruflo init --codex`
- `runtime`
  - Creates the runnable RuFlo runtime such as `.claude-flow/config.yaml`
  - Command: `ruflo init --minimal --force`

## Recommended order

1. If Codex integration is missing, initialize `codex`
2. If runtime is missing but orchestration backend is requested, initialize `runtime`
3. If both are already present, do not reinitialize unless the user explicitly asks

## Helper asset

Use `skills/multi-codex-orchestration/scripts/ensure_ruflo_init.py` to:
- detect current state
- choose `codex` vs `runtime`
- optionally execute the chosen `ruflo init` command

## Fallback

If `ruflo init` cannot be executed or fails:
- keep `tgtool` as the entrypoint
- fall back to the Phase 1 `codex-native wrapper`
- only use `claude-flow`/`ruflo` as an external backend when the runtime is actually available
