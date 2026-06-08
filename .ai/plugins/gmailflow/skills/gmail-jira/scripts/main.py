"""CLI entry point for turning one Gmail message into a Jira proposal or draft reply."""

from __future__ import annotations

import sys
from pathlib import Path

_JIRAFLOW_ROOT = Path(__file__).resolve().parents[4] / "jiraflow"
if str(_JIRAFLOW_ROOT) not in sys.path:
    sys.path.insert(0, str(_JIRAFLOW_ROOT))

import argparse
import json
from typing import Any

from actions import create_reply_draft, upload_attachments
from email_content import (
    classify_attachment,
    collect_attachments,
    extract_text,
)
from errors import build_error, require_choice
from gmail_client import GmailClient
from proposal_builder import (
    choose_component,
    choose_issue_type,
    header_map,
)
from shared.common import JiraCreateConfigStore, load_env
from shared.create_flow import (
    JIRA_VARS,
    build_issue_fields,
    create_issue_from_proposal,
    load_create_context,
    load_jira_client,
    missing_vars,
)
from shared.jira_api import JiraClient

GMAIL_VARS = [
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "GMAIL_ACCOUNT",
]

def _extract_email(addr: str) -> str:
    """Extract bare email from 'Name <email>' format."""
    return addr.split("<")[-1].rstrip(">").strip().lower() if "<" in addr else addr.strip().lower()

def _reply_recipients(
    sender: str, own_email: str, to_raw: str, cc_raw: str
) -> dict[str, str]:
    """Build To + Cc for reply-all, including sender, excluding own address."""
    own = own_email.lower()
    addrs = [sender] if sender else []
    addrs += [a.strip() for a in to_raw.split(",") if a.strip()]
    to_list: list[str] = []
    seen: set[str] = set()
    for a in addrs:
        key = _extract_email(a)
        if key == own or key in seen:
            continue
        seen.add(key)
        to_list.append(a)
    cc_list = [a.strip() for a in cc_raw.split(",") if a.strip() and _extract_email(a) != own]
    cc_list = [a for a in cc_list if _extract_email(a) not in seen]
    return {"to": ", ".join(to_list), "cc": ", ".join(cc_list)}

def build_parser() -> argparse.ArgumentParser:
    """Build CLI args for proposal, issue creation, and draft creation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--message-id", required=True)
    parser.add_argument("--project", default="")
    parser.add_argument("--component", default="")
    parser.add_argument("--issue-type", default="")
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--create-draft", action="store_true")
    parser.add_argument("--upload-attachments", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--issue-key", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--environment", default="")
    parser.add_argument("--estimate", type=int, default=0)
    parser.add_argument("--description", default="")
    parser.add_argument("--description-file", default="")
    parser.add_argument("--reply-body", default="")
    parser.add_argument("--json", action="store_true")
    return parser

def load_clients(
    repo_root: Path,
) -> tuple[JiraCreateConfigStore, GmailClient, JiraClient]:
    """Load repo-local env and API clients for the gmail-jira flow."""
    gmail_env = load_env(repo_root / ".env.gmail")
    _, jira_store, jira_client = load_jira_client(repo_root)
    return (
        jira_store,
        GmailClient(gmail_env),
        jira_client,
    )

def load_message_details(message: dict[str, Any]) -> dict[str, Any]:
    """Extract headers, body text, and attachment metadata from one Gmail message."""
    headers = header_map(message.get("payload", {}).get("headers", []))
    sender = headers.get("from", "")
    sender_email = sender.split("<")[-1].rstrip(">") if "<" in sender else sender
    body_text = extract_text(message.get("payload", {})).strip()
    attachments = collect_attachments(message.get("payload", {}))
    analyzed = []
    for item in attachments:
        enriched = dict(item)
        enriched["action"] = classify_attachment(item)
        analyzed.append(enriched)
    to_raw = headers.get("to", "")
    cc_raw = headers.get("cc", "")
    return {
        "subject": headers.get("subject", ""),
        "from": sender,
        "sender_email": sender_email.strip(),
        "message_id_header": headers.get("message-id", ""),
        "reply_to": headers.get("reply-to") or sender,
        "to_raw": to_raw,
        "cc_raw": cc_raw,
        "body_text": body_text,
        "attachments": analyzed,
    }

LoadJiraCtxResult = tuple[
    dict[str, str],
    dict[str, str],
    dict[str, Any] | None,
    dict[str, str | None],
    list[str],
]

def load_jira_context(
    jira_client: JiraClient,
    store: JiraCreateConfigStore,
    project_key: str,
    component_name: str,
    issue_type_name: str,
) -> LoadJiraCtxResult:
    """Resolve Jira issue type, component, sprint, and custom field metadata."""
    project = jira_client.get_project(project_key)
    issue_type = require_choice(
        choose_issue_type(project, issue_type_name),
        "issue type",
    )
    component = require_choice(
        choose_component(project, component_name),
        "component",
    )
    sprint, fields, missing = load_create_context(
        jira_client,
        store,
        project_key,
        issue_type["id"],
    )
    return issue_type, component, sprint, fields, missing

def assemble_proposal(
    args: argparse.Namespace,
    message: dict[str, Any],
    message_info: dict[str, Any],
    issue_type: dict[str, str],
    component: dict[str, str],
    sprint: dict[str, Any] | None,
    fields: dict[str, str | None],
    missing: list[str],
) -> dict[str, Any]:
    """Assemble the final proposal payload from parsed Gmail and Jira metadata."""
    desc_raw = getattr(args, "description", "")
    if not desc_raw:
        desc_file = getattr(args, "description_file", "")
        if desc_file:
            try:
                desc_raw = Path(desc_file).read_text(encoding="utf-8")
            except OSError:
                desc_raw = ""
    return {
        "ok": True,
        "project": args.project,
        "issue_type": issue_type,
        "component": component,
        "sprint": sprint,
        "jira_fields": fields,
        "message": {
            "id": message.get("id"),
            "thread_id": message.get("threadId"),
            **message_info,
        },
        "attachments": message_info["attachments"],
        "summary": args.summary,
        "environment": args.environment,
        "estimate_hours": args.estimate or None,
        "description": json.loads(desc_raw) if desc_raw else None,
        "reply_preview": args.reply_body,
        "warnings": [f"Skipped Jira field: {item}" for item in missing],
    }

def build_proposal(args: argparse.Namespace) -> dict[str, Any]:
    """Build a proposal payload from one Gmail message and Jira metadata."""
    repo_root = Path(__file__).resolve().parents[6]
    gmail_env = load_env(repo_root / ".env.gmail")
    jira_env = load_env(repo_root / ".env.jira")
    missing = missing_vars(gmail_env, GMAIL_VARS) + missing_vars(jira_env, JIRA_VARS)
    if missing:
        return build_error("Auth setup incomplete.", missing)

    args.project = args.project or jira_env.get("JIRA_PROJECT_KEY", "")
    if not args.project:
        return build_error("Project key required.", ["--project or JIRA_PROJECT_KEY"])

    store, gmail_client, jira_client = load_clients(repo_root)
    message = gmail_client.get_message(args.message_id)
    message_info = load_message_details(message)
    message_info["reply_to_all"] = _reply_recipients(message_info.get("from", ""), gmail_env.get("GMAIL_ACCOUNT", ""), message_info.pop("to_raw", ""), message_info.pop("cc_raw", ""))
    try:
        issue_type, component, sprint, fields, warnings = load_jira_context(jira_client, store, args.project, args.component, args.issue_type)
    except ValueError as error:
        return build_error(str(error))
    return assemble_proposal(args, message, message_info, issue_type, component, sprint, fields, warnings)

def apply_side_effects(
    args: argparse.Namespace,
    repo_root: Path,
    proposal: dict[str, Any],
    payload: dict[str, Any],
) -> None:
    """Apply Jira create, attachment upload, and draft creation steps."""
    issue_key = args.issue_key
    errors: list[dict[str, str]] = []
    if args.create:
        try:
            created = create_issue_from_proposal(repo_root, proposal)
            payload["created_issue"] = created
            issue_key = created.get("key", issue_key)
        except Exception as exc:
            errors.append({"step": "create_issue", "error": str(exc)})
    if args.upload_attachments:
        try:
            payload["uploaded_attachments"] = upload_attachments(
                repo_root,
                args.message_id,
                issue_key,
                proposal.get("attachments", []),
            )
        except Exception as exc:
            errors.append({"step": "upload_attachments", "error": str(exc)})
    if args.create_draft:
        try:
            payload["created_draft"] = create_reply_draft(
                repo_root,
                args.message_id,
                args.reply_body,
                proposal,
            )
        except Exception as exc:
            errors.append({"step": "create_draft", "error": str(exc)})
    if errors:
        payload["errors"] = errors

def main() -> int:
    """Run proposal mode by default, with optional Jira issue and Gmail draft creation."""
    args = build_parser().parse_args()
    proposal = build_proposal(args)
    if not proposal.get("ok"):
        print(json.dumps(proposal, indent=2))
        return 1
    repo_root = Path(__file__).resolve().parents[6]
    payload: dict[str, Any] = {"proposal": proposal}
    if args.dry_run:
        payload["dry_run"] = {
            "create_issue_fields": build_issue_fields(proposal)
            if args.create
            else None,
            "attachment_candidates": proposal.get("attachments", []),
            "reply_draft_preview": (
                proposal.get("reply_preview") if args.create_draft else None
            ),
        }
        print(json.dumps(payload, indent=2))
        return 0
    apply_side_effects(args, repo_root, proposal, payload)
    print(json.dumps(payload, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
