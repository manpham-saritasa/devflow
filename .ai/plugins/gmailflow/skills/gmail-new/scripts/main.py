"""CLI entry point for reading Gmail messages and project-labeled inbox slices."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gmail_client import GmailClient
from googleapiclient.errors import HttpError  # type: ignore[reportMissingImports]
from project_labels import GmailProjectLabelStore

REQUIRED_VARS = [
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "GMAIL_ACCOUNT",
]


def load_env(env_path: Path) -> dict[str, str]:
    """Load simple KEY=VALUE pairs from the Gmail env file."""
    data: dict[str, str] = {}
    if not env_path.exists():
        return data
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for GmailFlow reads."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("project", nargs="?", default="")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--query", default="is:unread")
    parser.add_argument("--projects", default="")
    parser.add_argument("--project-labels", action="store_true", default=True)
    parser.add_argument(
        "--no-project-labels", action="store_false", dest="project_labels"
    )
    parser.add_argument("--list-labels", action="store_true")
    return parser


def parse_projects(project: str, projects_csv: str) -> list[str]:
    """Normalize positional and CSV project inputs into unique project keys."""
    items: list[str] = []
    if project:
        items.append(project.strip().upper())
    if projects_csv:
        items.extend(
            [item.strip().upper() for item in projects_csv.split(",") if item.strip()]
        )
    return list(dict.fromkeys(items))


def load_project_label_map(
    repo_root: Path,
    projects: list[str],
    use_project_labels: bool,
) -> tuple[GmailProjectLabelStore, dict[str, dict[str, str]]]:
    """Load and optionally filter project-to-label mappings for this run."""
    label_store = GmailProjectLabelStore(repo_root)
    project_label_map = label_store.load() if use_project_labels else {}
    if projects and project_label_map:
        project_label_map = {
            key: value for key, value in project_label_map.items() if key in projects
        }
    return label_store, project_label_map


def make_missing_env_payload(repo_root: Path, missing: list[str]) -> dict[str, object]:
    """Build a consistent error payload for incomplete Gmail auth setup."""
    return {
        "ok": False,
        "message": "Gmail auth setup incomplete.",
        "env_file": str((repo_root / ".env.gmail").relative_to(repo_root)),
        "missing": missing,
    }


def run(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    """Execute the requested GmailFlow action and return exit code plus payload."""
    repo_root = Path(__file__).resolve().parents[6]
    env = load_env(repo_root / ".env.gmail")
    missing = [key for key in REQUIRED_VARS if not env.get(key)]
    if missing:
        return 1, make_missing_env_payload(repo_root, missing)

    projects = parse_projects(args.project, args.projects)
    use_project_labels = args.project_labels or bool(projects)
    label_store, project_label_map = load_project_label_map(
        repo_root, projects, use_project_labels
    )
    client = GmailClient(env)

    if args.list_labels:
        labels = client.list_labels()
        return 0, {
            "ok": True,
            "account": env["GMAIL_ACCOUNT"],
            "count": len(labels),
            "labels": labels,
        }
    if project_label_map:
        return 0, client.fetch_messages_by_project_labels(
            args.query,
            args.max_results,
            project_label_map,
            label_store,
        )
    return 0, client.fetch_messages(args.query, args.max_results)


def print_text_payload(payload: dict[str, object]) -> None:
    """Render a successful payload in the plain-text CLI format."""
    print(f"Account: {payload['account']}")
    labels = payload.get("labels")
    if isinstance(labels, dict):
        print(f"Labels: {payload['count']}")
        for name, label_id in sorted(labels.items()):
            print(f"- {name} => {label_id}")
        return
    print(f"Messages: {payload['count']}")
    project_labels = payload.get("project_label_filter")
    if isinstance(project_labels, dict) and project_labels:
        pairs = [f"{k}={v}" for k, v in project_labels.items()]
        print(f"Project labels: {', '.join(pairs)}")
    messages = payload.get("messages")
    if not isinstance(messages, list):
        return
    for idx, item in enumerate(messages, start=1):
        if not isinstance(item, dict):
            continue
        print(f"{idx}. {item['subject']}")
        print(f"   From: {item['from']}")
        print(f"   Date: {item['date']}")
        matched_projects = item.get("matched_projects")
        if matched_projects:
            print(f"   Projects: {', '.join(matched_projects)}")
        matched_labels = item.get("matched_labels")
        if matched_labels:
            print(f"   Labels: {', '.join(matched_labels)}")
        if item.get("snippet"):
            print(f"   Snippet: {item['snippet']}")


def main() -> int:
    """Parse arguments, execute the request, and print the selected output."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        code, payload = run(args)
    except HttpError as exc:
        code = 1
        payload = {
            "ok": False,
            "message": "Gmail API request failed.",
            "status": getattr(exc.resp, "status", None),
            "details": str(exc),
        }
    except Exception as exc:
        code = 1
        payload = {
            "ok": False,
            "message": "Unexpected Gmail error.",
            "details": str(exc),
        }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if code != 0:
            print(payload["message"])
        else:
            print_text_payload(payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
