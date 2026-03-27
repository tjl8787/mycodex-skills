#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


def detect_state(project_dir: Path) -> dict:
    codex_initialized = (
        (project_dir / 'AGENTS.md').exists()
        and (project_dir / '.agents' / 'config.toml').exists()
    )
    runtime_initialized = (project_dir / '.claude-flow' / 'config.yaml').exists()
    return {
        'project_dir': str(project_dir),
        'codex_initialized': codex_initialized,
        'runtime_initialized': runtime_initialized,
    }


def command_for_target(target: str) -> list[str]:
    if target == 'codex':
        return ['ruflo', 'init', '--codex']
    if target == 'runtime':
        return ['ruflo', 'init', '--minimal', '--force']
    raise ValueError(f'unsupported target: {target}')


def recommend_target(state: dict) -> str:
    if not state['codex_initialized']:
        return 'codex'
    if not state['runtime_initialized']:
        return 'runtime'
    return 'none'


def run_command(project_dir: Path, cmd: list[str]) -> int:
    shell_cmd = (
        'source /home/jetio/.nvm/nvm.sh '
        '&& nvm use 20 >/dev/null '
        f"&& cd {project_dir} && {' '.join(cmd)}"
    )
    return subprocess.run(['/bin/bash', '-lc', shell_cmd]).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Check or initialize Ruflo integration/runtime for a project.'
    )
    parser.add_argument('--project-dir', default='.')
    parser.add_argument(
        '--target',
        choices=['auto', 'codex', 'runtime'],
        default='auto',
        help='codex = AGENTS/.agents integration, runtime = .claude-flow runtime',
    )
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    state = detect_state(project_dir)
    target = args.target
    if target == 'auto':
        target = recommend_target(state)

    result = {
        **state,
        'requested_target': args.target,
        'selected_target': target,
        'action_needed': target != 'none',
        'recommended_command': None,
        'executed': False,
        'exit_code': 0,
    }

    if target != 'none':
        cmd = command_for_target(target)
        result['recommended_command'] = (
            'source /home/jetio/.nvm/nvm.sh && nvm use 20 >/dev/null && cd '
            + str(project_dir)
            + ' && '
            + ' '.join(cmd)
        )
        if args.execute:
            result['executed'] = True
            result['exit_code'] = run_command(project_dir, cmd)

    print(json.dumps(result, indent=2, sort_keys=True))
    return int(result['exit_code'])


if __name__ == '__main__':
    sys.exit(main())
