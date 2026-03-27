#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Build a Phase 2 claude-flow backend payload from a normalized orchestration session file.")
    parser.add_argument("session_file")
    parser.add_argument("--output")
    args = parser.parse_args()

    session = json.loads(Path(args.session_file).read_text(encoding="utf-8"))
    payload = {
        "backend": "claude-flow",
        "orchestration_session_id": session["orchestration_session_id"],
        "task_summary": session["task_summary"],
        "requested_outcome": session["requested_outcome"],
        "constraints": session.get("constraints", []),
        "candidate_roles": [item["role"] for item in session.get("roles", [])],
        "role_ownership": {
            item["role"]: {
                "ownership": item.get("ownership", item["role"]),
                "write_scope": item.get("write_scope", []),
            }
            for item in session.get("roles", [])
        },
        "support_layers": session.get("support_layers", []),
    }
    if "evidence_snapshot" in session:
        payload["evidence_snapshot"] = session["evidence_snapshot"]
    text = json.dumps(payload, indent=2, ensure_ascii=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
