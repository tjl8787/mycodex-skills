#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, text=True)


def load_state(project_dir: Path, session_name: str) -> dict:
    state_path = project_dir / ".codex-tmux" / f"{session_name}.json"
    if not state_path.exists():
        raise SystemExit(f"tmux state file not found: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dispatch a role-specific message into a tmux-visible orchestration pane."
    )
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--session-name", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--prefix", default="MAIN SESSION")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    state = load_state(Path(args.project_dir).resolve(), args.session_name)
    target = state.get("role_targets", {}).get(args.role)
    if not target:
        raise SystemExit(f"role target not found for: {args.role}")

    title = f"{args.role}: {args.message}".replace("\n", " ").strip()
    if len(title) > 60:
        title = title[:57] + "..."
    run(["tmux", "select-pane", "-t", target, "-T", title])

    banner = (
        f'printf "\\n=== {args.prefix}: {args.role.upper()} ===\\n%s\\n\\n" '
        f"{shlex.quote(args.message)}"
    )
    run(["tmux", "send-keys", "-t", target, banner, "C-m"])

    result = {
        "ok": True,
        "session_name": args.session_name,
        "role": args.role,
        "target": target,
        "message": args.message,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(f"dispatched: {args.role} -> {target}")


if __name__ == "__main__":
    main()
