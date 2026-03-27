#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_write_scope(values):
    result = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"invalid --write-scope value: {value}")
        role, raw_paths = value.split("=", 1)
        paths = [p for p in raw_paths.split(",") if p]
        result[role] = paths
    return result


def build_session(args):
    session_id = args.session_id or datetime.now(timezone.utc).strftime("orch-%Y%m%d-%H%M%S")
    write_scope_map = parse_write_scope(args.write_scope)
    roles = []
    for role in args.role:
        roles.append(
            {
                "role": role,
                "agent_id": None,
                "status": "pending",
                "ownership": args.ownership.get(role, role),
                "write_scope": write_scope_map.get(role, []),
                "last_summary": "not started",
            }
        )

    session = {
        "orchestration_session_id": session_id,
        "backend": "codex-native",
        "workspace_path": args.workspace_path,
        "task_summary": args.task_summary,
        "requested_outcome": args.requested_outcome,
        "constraints": args.constraint,
        "roles": roles,
        "status": "running",
        "summary": "session bootstrapped",
    }
    if args.support_layer:
        session["support_layers"] = args.support_layer
    if args.evidence_snapshot:
        session["evidence_snapshot"] = args.evidence_snapshot
    return session


def main():
    parser = argparse.ArgumentParser(description="Bootstrap a Phase 1 codex-native orchestration session file.")
    parser.add_argument("--task-summary", required=True)
    parser.add_argument("--workspace-path", required=True)
    parser.add_argument("--requested-outcome", required=True)
    parser.add_argument("--role", action="append", default=[])
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--support-layer", action="append", default=[])
    parser.add_argument("--evidence-snapshot")
    parser.add_argument("--session-id")
    parser.add_argument("--write-scope", action="append", default=[])
    parser.add_argument("--ownership", action="append", default=[])
    parser.add_argument("--output")
    args = parser.parse_args()

    if not args.role:
        parser.error("at least one --role is required")

    ownership_map = {}
    for item in args.ownership:
        if "=" not in item:
            parser.error(f"invalid --ownership value: {item}")
        role, ownership = item.split("=", 1)
        ownership_map[role] = ownership
    args.ownership = ownership_map

    session = build_session(args)
    text = json.dumps(session, indent=2, ensure_ascii=True)
    if args.output:
        output = Path(args.output)
        output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
