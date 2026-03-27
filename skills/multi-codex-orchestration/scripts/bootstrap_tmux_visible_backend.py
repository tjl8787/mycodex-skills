#!/usr/bin/env python3
import argparse
import json
import shlex
import shutil
import subprocess
from pathlib import Path


DEFAULT_ROLES = ["planner", "implementer", "verifier", "reviewer"]


def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        capture_output=capture,
    )


def session_exists(session_name: str) -> bool:
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        text=True,
        capture_output=True,
    )
    return result.returncode == 0


def configure_tmux_session(session_name: str) -> None:
    run(["tmux", "set-option", "-t", session_name, "-g", "mouse", "on"])
    run(["tmux", "set-option", "-t", session_name, "-s", "set-clipboard", "on"])


def list_panes(session_name: str) -> list[str]:
    return (
        run(
            ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_index}"],
            capture=True,
        )
        .stdout.strip()
        .splitlines()
    )


def pane_current_command(session_name: str, pane: str) -> str:
    return (
        run(
            [
                "tmux",
                "display-message",
                "-p",
                "-t",
                f"{session_name}:0.{pane}",
                "#{pane_current_command}",
            ],
            capture=True,
        )
        .stdout.strip()
    )


def build_role_prompt(
    role: str, project_dir: Path, task_summary: str | None, requested_outcome: str | None
) -> str:
    parts = [
        f"你是当前可见多agent会话里的 {role} 角色。",
        f"工作目录是 {project_dir}。",
    ]
    if task_summary:
        parts.append(f"当前任务：{task_summary}")
    if requested_outcome:
        parts.append(f"目标结果：{requested_outcome}")
    parts.append("先确认你的角色和工作边界，然后等待或继续处理与你角色匹配的工作。")
    return " ".join(parts)


def launch_codex_worker(
    session_name: str,
    pane: str,
    role: str,
    project_dir: Path,
    task_summary: str | None,
    requested_outcome: str | None,
) -> None:
    current = pane_current_command(session_name, pane)
    if current in {"node", "codex"}:
        return

    prompt = build_role_prompt(role, project_dir, task_summary, requested_outcome)
    command = f"codex {shlex.quote(prompt)}"
    run(["tmux", "send-keys", "-t", f"{session_name}:0.{pane}", command, "C-m"])


def build_layout(
    session_name: str,
    roles: list[str],
    project_dir: Path,
    task_summary: str | None,
    requested_outcome: str | None,
    launch_codex: bool,
) -> dict[str, str]:
    # session starts with pane 0
    while True:
        pane_count = len(list_panes(session_name))
        if pane_count >= len(roles):
            break
        run(["tmux", "split-window", "-t", session_name, "-d"])
        run(["tmux", "select-layout", "-t", session_name, "tiled"])

    panes = list_panes(session_name)

    role_map: dict[str, str] = {}

    for pane, role in zip(panes, roles):
        target = f"{session_name}:0.{pane}"
        role_map[role] = target
        banner = f'printf "\\n=== {role.upper()} ===\\nworkspace: %s\\n\\n" "{project_dir}"'
        run(["tmux", "send-keys", "-t", target, banner, "C-m"])
        run(["tmux", "select-pane", "-t", target, "-T", role])
        if launch_codex:
            launch_codex_worker(
                session_name,
                pane,
                role,
                project_dir,
                task_summary,
                requested_outcome,
            )
    return role_map


def state_file_path(project_dir: Path, session_name: str) -> Path:
    return project_dir / ".codex-tmux" / f"{session_name}.json"


def write_state(
    project_dir: Path,
    session_name: str,
    roles: list[str],
    role_map: dict[str, str],
    attach_command: str,
    launch_codex: bool,
) -> Path:
    path = state_file_path(project_dir, session_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "session_name": session_name,
        "backend": "tmux-visible",
        "project_dir": str(project_dir),
        "roles": roles,
        "role_targets": role_map,
        "attach_command": attach_command,
        "launch_codex": launch_codex,
    }
    path.write_text(json.dumps(state, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a visible tmux session for multi-codex orchestration."
    )
    parser.add_argument("--session-name", default="codex-swarm")
    parser.add_argument("--roles", nargs="*", default=DEFAULT_ROLES)
    parser.add_argument("--project-dir", default=str(Path.cwd()))
    parser.add_argument("--task-summary")
    parser.add_argument("--requested-outcome")
    parser.add_argument("--no-launch-codex", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if shutil.which("tmux") is None:
        raise SystemExit("tmux not found")

    project_dir = Path(args.project_dir).resolve()
    created = False

    if not session_exists(args.session_name):
        run(
            [
                "tmux",
                "new-session",
                "-d",
                "-s",
                args.session_name,
                "-c",
                str(project_dir),
            ]
        )
        created = True

    configure_tmux_session(args.session_name)

    role_map = build_layout(
        args.session_name,
        args.roles,
        project_dir,
        args.task_summary,
        args.requested_outcome,
        not args.no_launch_codex,
    )
    attach_command = f"tmux attach -t {args.session_name}"
    state_path = write_state(
        project_dir,
        args.session_name,
        args.roles,
        role_map,
        attach_command,
        not args.no_launch_codex,
    )

    result = {
        "ok": True,
        "backend": "tmux-visible",
        "session_name": args.session_name,
        "roles": args.roles,
        "created": created,
        "launch_codex": not args.no_launch_codex,
        "attach_command": attach_command,
        "state_file": str(state_path),
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(f"backend: {result['backend']}")
        print(f"session: {result['session_name']}")
        print(f"created: {str(result['created']).lower()}")
        print(f"roles: {', '.join(result['roles'])}")
        print(f"attach: {result['attach_command']}")


if __name__ == "__main__":
    main()
