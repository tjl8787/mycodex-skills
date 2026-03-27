#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a one-shot Codex task inside a tmux-visible shell pane."
    )
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--session-name", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--title")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    helper = (
        Path(__file__).resolve().parent / "execute_tmux_role_command.py"
    )
    title = args.title or f"{args.role}: codex task"
    command = f"codex {shlex.quote(args.prompt)}"
    result = subprocess.run(
        [
            "python3",
            str(helper),
            "--project-dir",
            str(project_dir),
            "--session-name",
            args.session_name,
            "--role",
            args.role,
            "--title",
            title,
            "--command",
            command,
            "--json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    payload["prompt"] = args.prompt
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(f"dispatched codex task: {args.role}")


if __name__ == "__main__":
    main()
