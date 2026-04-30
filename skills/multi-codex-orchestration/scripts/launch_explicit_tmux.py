#!/usr/bin/env python3
import argparse
import shlex
import subprocess
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def has_tmux_session(session: str) -> bool:
    proc = subprocess.run(
        ["tmux", "has-session", "-t", session],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def create_two_pane_session(session: str, cwd: Path) -> None:
    run(["tmux", "new-session", "-d", "-s", session, "-c", str(cwd)])
    run(["tmux", "split-window", "-h", "-t", f"{session}:0"])
    run(["tmux", "set", "-g", "mouse", "on"])
    run(["tmux", "set", "-g", "set-clipboard", "on"])
    run(["tmux", "setw", "-t", f"{session}:0", "synchronize-panes", "off"])
    run(
        [
            "tmux",
            "send-keys",
            "-t",
            f"{session}:0.0",
            "clear; echo '[operator] active execution pane'; pwd",
            "C-m",
        ]
    )
    run(
        [
            "tmux",
            "send-keys",
            "-t",
            f"{session}:0.1",
            "clear; echo '[critic] dormant by default (wake on failure/stage switch/review)'; pwd",
            "C-m",
        ]
    )


def try_open_foreground(session: str) -> str:
    if "TMUX" in __import__("os").environ:
        run(["tmux", "switch-client", "-t", session], check=False)
        return "switched current tmux client"

    env = __import__("os").environ
    if not env.get("DISPLAY"):
        return "no DISPLAY; foreground popup skipped"

    attach_cmd = f"tmux attach -t {shlex.quote(session)}"
    terminal_cmds = [
        ["x-terminal-emulator", "-e", "bash", "-lc", attach_cmd],
        ["gnome-terminal", "--", "bash", "-lc", attach_cmd],
        ["xfce4-terminal", "--command", f"bash -lc {shlex.quote(attach_cmd)}"],
        ["konsole", "-e", "bash", "-lc", attach_cmd],
        ["xterm", "-e", "bash", "-lc", attach_cmd],
    ]
    for cmd in terminal_cmds:
        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return f"opened terminal: {cmd[0]}"
        except FileNotFoundError:
            continue
        except Exception:
            continue

    return "failed to launch terminal emulator; manual attach required"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch a visible 2-pane tmux multi-agent session (operator + critic)."
    )
    parser.add_argument("--session", default="tgtool-visible")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--force-recreate", action="store_true")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    if args.force_recreate and has_tmux_session(args.session):
        run(["tmux", "kill-session", "-t", args.session], check=False)

    created = False
    if not has_tmux_session(args.session):
        create_two_pane_session(args.session, cwd)
        created = True

    open_result = try_open_foreground(args.session)
    print(
        "\n".join(
            [
                f"session={args.session}",
                f"created={str(created).lower()}",
                "panes=2 (operator, critic)",
                f"foreground={open_result}",
                f"manual_attach=tmux attach -t {args.session}",
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
