#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run_shell(project_dir: Path, command: str) -> subprocess.CompletedProcess:
    shell_cmd = (
        "source /home/jetio/.nvm/nvm.sh "
        "&& nvm use 20 >/dev/null "
        f"&& cd {project_dir} && {command}"
    )
    return subprocess.run(
        ["/bin/bash", "-lc", shell_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def parse_first(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1) if match else None


def record_step(steps: list[dict], step: str, command: str, proc: subprocess.CompletedProcess) -> dict:
    data = {
        "step": step,
        "command": command,
        "exit_code": proc.returncode,
        "ok": proc.returncode == 0,
        "output_tail": "\n".join(proc.stdout.splitlines()[-20:]),
    }
    steps.append(data)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe the local Ruflo CLI execution path.")
    parser.add_argument("--project-dir", default=".")
    parser.add_argument("--objective", default="Probe Ruflo local execution path")
    parser.add_argument("--agent-type", default="coder")
    parser.add_argument("--task-type", default="implementation")
    parser.add_argument("--task-description", default="Probe task created by Codex")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    bootstrap_script = Path(__file__).resolve().parent / "bootstrap_ruflo_backend.py"
    bootstrap_proc = subprocess.run(
        [sys.executable, str(bootstrap_script), "--project-dir", str(project_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    bootstrap_ok = bootstrap_proc.returncode == 0
    bootstrap_json = None
    if bootstrap_ok:
        try:
            bootstrap_json = json.loads(bootstrap_proc.stdout)
        except json.JSONDecodeError:
            bootstrap_ok = False

    steps: list[dict] = [{
        "step": "bootstrap",
        "command": f"{sys.executable} {bootstrap_script} --project-dir {project_dir}",
        "exit_code": bootstrap_proc.returncode,
        "ok": bootstrap_ok,
        "output_tail": "\n".join(bootstrap_proc.stdout.splitlines()[-20:]),
    }]

    swarm_id = None
    agent_id = None
    task_id = None

    ok = bootstrap_ok
    if ok:
        swarm_cmd = f"ruflo swarm start -o {json.dumps(args.objective)} -s development"
        swarm_proc = run_shell(project_dir, swarm_cmd)
        swarm_step = record_step(steps, "swarm_start", swarm_cmd, swarm_proc)
        swarm_id = parse_first(r"Swarm (swarm-[A-Za-z0-9_-]+) initialized", swarm_proc.stdout)
        swarm_step["swarm_id"] = swarm_id
        ok = swarm_step["ok"] and ok

    if ok:
        agent_cmd = f"ruflo agent spawn -t {args.agent_type}"
        agent_proc = run_shell(project_dir, agent_cmd)
        agent_step = record_step(steps, "agent_spawn", agent_cmd, agent_proc)
        agent_id = parse_first(r"\| ID\s+\|\s+(agent-[A-Za-z0-9_-]+)\s+\|", agent_proc.stdout)
        if not agent_id:
            agent_id = parse_first(r"(agent-[A-Za-z0-9_-]+)", agent_proc.stdout)
        agent_step["agent_id"] = agent_id
        ok = agent_step["ok"] and bool(agent_id) and ok

    if ok:
        task_cmd = f"ruflo task create -t {args.task_type} -d {json.dumps(args.task_description)}"
        task_proc = run_shell(project_dir, task_cmd)
        task_step = record_step(steps, "task_create", task_cmd, task_proc)
        task_id = parse_first(r"Task created: (task-[A-Za-z0-9_-]+)", task_proc.stdout)
        task_step["task_id"] = task_id
        ok = task_step["ok"] and bool(task_id) and ok

    if ok:
        assign_cmd = f"ruflo task assign {task_id} --agent {agent_id}"
        assign_proc = run_shell(project_dir, assign_cmd)
        assign_step = record_step(steps, "task_assign", assign_cmd, assign_proc)
        assign_step["task_id"] = task_id
        assign_step["agent_id"] = agent_id
        ok = assign_step["ok"] and ok

    result = {
        "ok": ok,
        "project_dir": str(project_dir),
        "bootstrap": bootstrap_json,
        "swarm_id": swarm_id,
        "agent_id": agent_id,
        "task_id": task_id,
        "steps": steps,
        "notes": [
            "This probe validates the local Ruflo CLI boundary only.",
            "Actual in-session multi-agent execution should still prefer claude_flow MCP tools after bootstrap.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
