#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Normalize a Phase 2 claude-flow backend result into the stable orchestration adapter shape.")
    parser.add_argument("result_file")
    parser.add_argument("--output")
    args = parser.parse_args()

    raw = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
    normalized = {
        "orchestration_session_id": raw["orchestration_session_id"],
        "backend": "claude-flow",
        "roles_spawned": raw.get("roles_spawned", []),
        "status": raw.get("status", "failed"),
        "role_statuses": raw.get("role_statuses", []),
        "summary": raw.get("summary", "")
    }
    for optional in ("artifacts", "blockers", "fallback_reason", "handoff_recommendation"):
        if optional in raw:
            normalized[optional] = raw[optional]
    text = json.dumps(normalized, indent=2, ensure_ascii=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
