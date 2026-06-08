"""CLI entry for Jira-side issue creation helpers."""

from __future__ import annotations

import sys
from pathlib import Path

_JIRAFLOW_ROOT = Path(__file__).resolve().parents[3]
if str(_JIRAFLOW_ROOT) not in sys.path:
    sys.path.insert(0, str(_JIRAFLOW_ROOT))

import argparse
import json

from shared.create_flow import (
    JIRA_VARS,
    create_issue_from_proposal,
    load_env,
    missing_vars,
)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI args for simple proposal-based issue creation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal", required=True)
    return parser


def main() -> int:
    """Create Jira issue from proposal JSON file path."""
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[6]
    jira_env = load_env(repo_root / ".env.jira")
    missing = missing_vars(jira_env, JIRA_VARS)
    if missing:
        print(
            json.dumps(
                {"ok": False, "message": "Auth setup incomplete.", "missing": missing},
                indent=2,
            )
        )
        return 1
    proposal = json.loads(Path(args.proposal).read_text(encoding="utf-8"))
    created = create_issue_from_proposal(repo_root, proposal)
    print(json.dumps({"ok": True, "created_issue": created}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
