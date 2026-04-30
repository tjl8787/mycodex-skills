#!/usr/bin/env python3
"""Temporarily enable disabled Codex skills and reset afterward."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

HOME = Path.home()
DEFAULT_CONFIGS = [
    HOME / ".codex" / "config.toml",
    HOME / ".codex" / "config.chatgpt.toml",
]
DEFAULT_STATE_FILE = HOME / ".codex" / "skill-temp-state.json"

BLOCK_RE = re.compile(
    r'\[\[skills\.config\]\]\n'
    r'path = "(?P<path>[^"]+)"\n'
    r'enabled = (?P<enabled>true|false)'
)


@dataclass
class Change:
    config: str
    skill: str
    from_state: str
    to_state: str


def read_state(state_file: Path) -> Dict:
    if not state_file.exists():
        return {"version": 1, "changes": {}, "updated_at": None}
    return json.loads(state_file.read_text())


def write_state(state_file: Path, data: Dict) -> None:
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    state_file.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n")


def skill_path(skill: str) -> str:
    return str(HOME / ".codex" / "skills" / skill / "SKILL.md")


def update_skill_state_in_text(text: str, skill: str, target: str) -> Tuple[str, List[str]]:
    target_path = skill_path(skill)
    seen_states: List[str] = []

    def repl(match: re.Match) -> str:
        path = match.group("path")
        enabled = match.group("enabled")
        if path == target_path:
            seen_states.append(enabled)
            return match.group(0).replace(f"enabled = {enabled}", f"enabled = {target}")
        return match.group(0)

    new_text = BLOCK_RE.sub(repl, text)
    return new_text, seen_states


def command_on(skills: List[str], configs: List[Path], state_file: Path) -> int:
    state = read_state(state_file)
    state_changes = state.setdefault("changes", {})
    changes: List[Change] = []

    for cfg in configs:
        if not cfg.exists():
            continue
        text = cfg.read_text()
        original_text = text

        for skill in skills:
            text, seen = update_skill_state_in_text(text, skill, "true")
            if not seen:
                continue
            if all(s == "false" for s in seen):
                state_changes.setdefault(str(cfg), {})[skill] = "false"
            if any(s != "true" for s in seen):
                before = "mixed" if len(set(seen)) > 1 else seen[0]
                changes.append(Change(str(cfg), skill, before, "true"))

        if text != original_text:
            cfg.write_text(text)

    write_state(state_file, state)

    if not changes:
        print("No config values changed.")
        return 0

    for c in changes:
        print(f"ON: {c.skill} | {c.config} | {c.from_state} -> {c.to_state}")
    return 0


def command_reset(configs: List[Path], state_file: Path) -> int:
    state = read_state(state_file)
    state_changes = state.get("changes", {})
    reverted = 0

    for cfg in configs:
        skill_states = state_changes.get(str(cfg), {})
        if not skill_states or not cfg.exists():
            continue

        text = cfg.read_text()
        original_text = text

        for skill, prev_state in skill_states.items():
            text, seen = update_skill_state_in_text(text, skill, prev_state)
            if seen:
                reverted += 1

        if text != original_text:
            cfg.write_text(text)

    write_state(state_file, {"version": 1, "changes": {}, "updated_at": None})
    print(f"Reset complete. Reverted {reverted} skill entries.")
    return 0


def command_status(configs: List[Path], state_file: Path) -> int:
    state = read_state(state_file)
    print(f"State file: {state_file}")
    print(json.dumps(state, ensure_ascii=True, indent=2))
    print("\nConfig scan:")

    for cfg in configs:
        print(f"- {cfg}")
        if not cfg.exists():
            print("  missing")
            continue
        text = cfg.read_text()
        blocks = BLOCK_RE.findall(text)
        print(f"  skills.config blocks: {len(blocks)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Temporary skill toggles for Codex config.")
    parser.add_argument(
        "--config",
        action="append",
        default=[],
        help="Config file path. Can pass multiple times. Default: ~/.codex/config.toml and config.chatgpt.toml",
    )
    parser.add_argument(
        "--state-file",
        default=str(DEFAULT_STATE_FILE),
        help="Path to state JSON file. Default: ~/.codex/skill-temp-state.json",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_on = sub.add_parser("on", help="Temporarily enable one or more skill ids.")
    p_on.add_argument("skills", nargs="+", help="Skill directory names, e.g. systematic-debugging")

    sub.add_parser("reset", help="Reset skills changed by previous 'on' back to original state.")
    sub.add_parser("status", help="Show state and basic config scan.")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configs = [Path(c).expanduser() for c in args.config] if args.config else DEFAULT_CONFIGS
    state_file = Path(args.state_file).expanduser()

    try:
        if args.cmd == "on":
            return command_on(args.skills, configs, state_file)
        if args.cmd == "reset":
            return command_reset(configs, state_file)
        if args.cmd == "status":
            return command_status(configs, state_file)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "Hint: ensure target config/state paths are writable, or run with appropriate permissions.",
            file=sys.stderr,
        )
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
