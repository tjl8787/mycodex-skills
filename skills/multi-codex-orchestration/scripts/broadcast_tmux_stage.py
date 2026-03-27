#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


DEFAULT_STAGE_PROMPTS = {
    "planner": "主会话：进入规划阶段，请拆分任务、梳理边界和风险。",
    "implementer": "主会话：进入实现阶段，只处理分配给你的实现范围。",
    "verifier": "主会话：进入验证阶段，请聚焦检查、测试和结果核对。",
    "reviewer": "主会话：进入审查阶段，请评估质量、风险和遗漏。",
}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, text=True)


def load_state(project_dir: Path, session_name: str) -> dict:
    state_path = project_dir / ".codex-tmux" / f"{session_name}.json"
    if not state_path.exists():
        raise SystemExit(f"tmux state file not found: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def dispatch(target: str, role: str, message: str, prefix: str) -> None:
    title = f"{role}: {message}".replace("\n", " ").strip()
    if len(title) > 60:
        title = title[:57] + "..."
    run(["tmux", "select-pane", "-t", target, "-T", title])
    banner = (
        f'printf "\\n=== {prefix}: {role.upper()} ===\\n%s\\n\\n" '
        f'{json.dumps(message)}'
    )
    run(["tmux", "send-keys", "-t", target, banner, "C-m"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Broadcast a main-session stage update to all tmux-visible role panes."
    )
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--session-name", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--message")
    parser.add_argument("--prefix", default="MAIN SESSION")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    state = load_state(Path(args.project_dir).resolve(), args.session_name)
    role_targets = state.get("role_targets", {})
    base_message = args.message or f"主会话：切换到 {args.stage} 阶段。"

    dispatched = []
    for role, target in role_targets.items():
        role_message = DEFAULT_STAGE_PROMPTS.get(role, base_message)
        if args.message:
            role_message = f"{base_message} 你的角色是 {role}。"
        dispatch(target, role, role_message, f"{args.prefix} / {args.stage}")
        dispatched.append({"role": role, "target": target, "message": role_message})

    result = {
        "ok": True,
        "session_name": args.session_name,
        "stage": args.stage,
        "dispatched": dispatched,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(f"broadcasted stage: {args.stage}")


if __name__ == "__main__":
    main()
