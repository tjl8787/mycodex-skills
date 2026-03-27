# Ruflo Runtime Bootstrap Playbook

Use this playbook when `tgtool` routes into `multi-codex orchestration` and the user wants the `ruflo` backend to be bootstrapped automatically.

## Default bootstrap chain

The default chain is:

1. ensure Codex integration exists
2. ensure runtime state exists
3. initialize a swarm
4. optionally start the daemon

Concrete commands:

- `ruflo init --codex`
- `ruflo init --minimal --force`
- `ruflo swarm init --v3-mode`
- optional: `ruflo daemon start`

## Recommended helper

Use `skills/multi-codex-orchestration/scripts/bootstrap_ruflo_backend.py` as the first executable backend bootstrap helper.

It should be preferred over manually piecing together the chain because it:
- checks current state first
- skips already-satisfied steps
- returns a stable JSON result shape
- keeps daemon startup optional

## Why daemon is optional

In local validation, `ruflo daemon start` can return success while later `daemon status` may still show a stopped state depending on environment behavior.

So the default automated backend chain should rely on:
- init
- swarm init
- status checks

and only add daemon startup when the caller explicitly wants it.

## Fallback

If bootstrap fails:
- keep `tgtool` as the top-level router
- fall back to the Phase 1 `codex-native wrapper`
- do not claim the external backend is ready until swarm initialization succeeded
