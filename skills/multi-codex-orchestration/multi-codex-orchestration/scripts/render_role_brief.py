#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def format_list(items, empty_text="(none)"):
    if not items:
        return empty_text
    return "\n".join(f"- {item}" for item in items)


def abbreviate_text(text, max_len=400):
    if not text:
        return ""
    text = str(text).strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + " ...[truncated]"


def main():
    parser = argparse.ArgumentParser(description="Render a role brief from a codex-native orchestration session file.")
    parser.add_argument("session_file")
    parser.add_argument("--role", required=True)
    parser.add_argument("--delta", action="store_true", help="Emit a delta brief based on last_summary + new instructions")
    parser.add_argument("--new-instructions", default="", help="Additional instructions for delta mode")
    parser.add_argument("--max-summary-chars", type=int, default=400, help="Maximum chars for long summaries in low-token mode")
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

    task_summary = session.get("task_summary", "")
    requested_outcome = session.get("requested_outcome", "")

    # Always generate in low-token mode by truncating long text and removing verbose metadata.
    task_summary = abbreviate_text(task_summary, max_len=args.max_summary_chars)
    requested_outcome = abbreviate_text(requested_outcome, max_len=args.max_summary_chars)
    constraints = "- <use minimal constraints; avoid repeating entire context>"
    support_layers = "- <use only essential support layers>"

    if args.delta:
        prev_summary = role_entry.get("last_summary", "<no previous summary available>")
        prev_summary = abbreviate_text(prev_summary, max_len=args.max_summary_chars)
        summary = f"""# Role Brief (Delta): {args.role}

## Previous Summary
{prev_summary}

## New Instructions
{args.new_instructions.strip() or '- none (status check only)'}

## Write Scope
{write_scope}

## Constraints
{constraints}

## Expected Output
- concise role summary
- blockers, if any
- relevant artifacts or files
- clear handoff status
"""
        print(summary.rstrip() + "\n")
        return

    brief = f"""# Role Brief: {args.role}

## Shared Task
{task_summary}

## Requested Outcome
{requested_outcome}

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
