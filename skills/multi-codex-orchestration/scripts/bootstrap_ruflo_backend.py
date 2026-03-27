#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_shell(project_dir: Path, command: str) -> subprocess.CompletedProcess:
    shell_cmd = (
        'source /home/jetio/.nvm/nvm.sh '
        '&& nvm use 20 >/dev/null '
        f'&& cd {project_dir} && {command}'
    )
    return subprocess.run(
        ['/bin/bash', '-lc', shell_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def detect_state(project_dir: Path) -> dict:
    return {
        'project_dir': str(project_dir),
        'codex_initialized': (project_dir / 'AGENTS.md').exists() and (project_dir / '.agents' / 'config.toml').exists(),
        'runtime_initialized': (project_dir / '.claude-flow' / 'config.yaml').exists(),
    }


def maybe_step(steps: list, name: str, command: str, project_dir: Path, enabled: bool = True) -> bool:
    if not enabled:
        steps.append({'step': name, 'skipped': True})
        return True
    proc = run_shell(project_dir, command)
    steps.append({
        'step': name,
        'command': command,
        'exit_code': proc.returncode,
        'ok': proc.returncode == 0,
        'output_tail': '\n'.join(proc.stdout.splitlines()[-20:]),
    })
    return proc.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Bootstrap a usable Ruflo backend for multi-codex orchestration.')
    parser.add_argument('--project-dir', default='.')
    parser.add_argument('--with-daemon', action='store_true')
    parser.add_argument('--skip-swarm', action='store_true')
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    steps = []
    state_before = detect_state(project_dir)

    ok = True
    if not state_before['codex_initialized']:
        ok = maybe_step(steps, 'init_codex', 'ruflo init --codex', project_dir) and ok
    else:
        steps.append({'step': 'init_codex', 'skipped': True, 'reason': 'already initialized'})

    state_mid = detect_state(project_dir)
    if ok and not state_mid['runtime_initialized']:
        ok = maybe_step(steps, 'init_runtime', 'ruflo init --minimal --force', project_dir) and ok
    else:
        steps.append({'step': 'init_runtime', 'skipped': True, 'reason': 'already initialized' if state_mid['runtime_initialized'] else 'prior step failed'})

    if ok:
        ok = maybe_step(steps, 'init_swarm', 'ruflo swarm init --v3-mode', project_dir, enabled=not args.skip_swarm) and ok
    else:
        steps.append({'step': 'init_swarm', 'skipped': True, 'reason': 'prior step failed'})

    if ok:
        maybe_step(steps, 'daemon_start', 'ruflo daemon start', project_dir, enabled=args.with_daemon)
    else:
        steps.append({'step': 'daemon_start', 'skipped': True, 'reason': 'prior step failed'})

    state_after = detect_state(project_dir)
    result = {
        'project_dir': str(project_dir),
        'ok': ok,
        'state_before': state_before,
        'state_after': state_after,
        'steps': steps,
        'recommended_next': 'ruflo swarm status' if ok and not args.skip_swarm else 'ruflo status',
        'notes': [
            'daemon_start is optional because local daemon persistence may vary by environment',
            'phase-1 tgtool integration can treat this helper as the default Ruflo bootstrap path',
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
