#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def format_list(items, empty_text="(none)"):
    if not items:
        return empty_text
    return "\n".join(f"- {item}" for item in items)


def main():
    parser = argparse.ArgumentParser(description="Render a role brief from a codex-native orchestration session file.")
    parser.add_argument("session_file")
    parser.add_argument("--role", required=True)
    args = parser.parse_args()

    session = json.loads(Path(args.session_file).read_text(encoding="utf-8"))
    role_entry = None
    for item in session.get("roles", []):
        if item.get("role") == args.role:
            role_entry = item
            break
    if role_entry is None:
        raise SystemExit(f"role not found: {args.role}")

    constraints = format_list(session.get("constraints", []))
    write_scope = format_list(role_entry.get("write_scope", []))
    support_layers = format_list(session.get("support_layers", []))
    brief = f"""# Role Brief: {args.role}

## Shared Task
{session.get('task_summary', '')}

## Requested Outcome
{session.get('requested_outcome', '')}

## Ownership
{role_entry.get('ownership', args.role)}

## Write Scope
{write_scope}

## Constraints
{constraints}

## Support Layers
{support_layers}

## Expected Output
- concise role summary
- blockers, if any
- relevant artifacts or files
- clear handoff status
"""
    print(brief.rstrip() + "\n")


if __name__ == "__main__":
    main()
