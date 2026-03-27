#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
from pathlib import Path


def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, capture_output=capture)


def load_state(project_dir: Path, session_name: str) -> dict:
    state_path = project_dir / ".codex-tmux" / f"{session_name}.json"
    if not state_path.exists():
        raise SystemExit(f"tmux state file not found: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute a real shell command inside a tmux-visible role pane."
    )
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--session-name", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--title")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    state = load_state(project_dir, args.session_name)
    target = state.get("role_targets", {}).get(args.role)
    if not target:
        raise SystemExit(f"role target not found for: {args.role}")
    pane_mode = state.get("pane_mode", "shell")
    if pane_mode != "shell":
        raise SystemExit(
            f"tmux role command execution requires shell panes; current pane_mode={pane_mode}"
        )

    title = (args.title or f"{args.role}: executing").replace("\n", " ").strip()
    if len(title) > 60:
        title = title[:57] + "..."
    run(["tmux", "select-pane", "-t", target, "-T", title])

    banner = (
        'printf "\\n=== MAIN SESSION / EXEC: %s ===\\n%s\\n\\n" '
        f"{shlex.quote(args.role.upper())} {shlex.quote(args.command)}"
    )
    run(["tmux", "send-keys", "-t", target, banner, "C-m"])
    run(
        [
            "tmux",
            "send-keys",
            "-t",
            target,
            f"cd {shlex.quote(str(project_dir))} && {args.command}",
            "C-m",
        ]
    )

    result = {
        "ok": True,
        "session_name": args.session_name,
        "role": args.role,
        "target": target,
        "command": args.command,
        "title": title,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(f"executed: {args.role} -> {target}")


if __name__ == "__main__":
    main()
