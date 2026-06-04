import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

TASK_KEY_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
PROJECT_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+$")
HTTP_TIMEOUT_SECONDS = 15
COMMAND_TIMEOUT_SECONDS = 20
NOISY_UPDATE_FIELDS = {
    "status",
    "rank",
    "sprint",
    "link",
    "attachment",
    "comment",
    "worklog",
}
ROLES = {"dev", "qa", "tm", "pm", "mixed"}
DEFAULT_STAGE_GROUPS = {
    "review": ["In Review", "Verify", "Code Review", "TM Review"],
    "qa": ["In QA", "Ready for QA", "QA Review", "Testing"],
    "active": ["In Progress", "On-going", "Ongoing", "Ready for Development"],
    "blocked": ["Blocked", "On Hold"],
}


if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def find_repo_root(start: str) -> str:
    path = os.path.dirname(os.path.abspath(start))
    while path and not os.path.exists(os.path.join(path, ".git")):
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent
    return path


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_jira_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z").astimezone(timezone.utc)


def parse_gh_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def fmt_dt(value: datetime | None) -> str:
    if value is None:
        return "?"
    return value.astimezone().strftime("%Y-%m-%d %H:%M")


def warn(message: str) -> None:
    print(f"[jira-day] {message}", file=sys.stderr)


def extract_task_keys(text: str) -> set[str]:
    return set(TASK_KEY_RE.findall(text or ""))


def extract_text(node: Any) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type == "text":
            return node.get("text", "")
        if node_type == "mention":
            return "@" + node.get("attrs", {}).get("text", "")
        if node_type == "hardBreak":
            return " "
        content = node.get("content", [])
        return " ".join(x for x in (extract_text(c) for c in content) if x)
    if isinstance(node, list):
        return " ".join(x for x in (extract_text(i) for i in node) if x)
    return ""


def run_command(args: list[str], cwd: str) -> str:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        warn(f"command timed out: {' '.join(args)}")
    except FileNotFoundError:
        warn(f"command not found: {args[0]}")
    except subprocess.CalledProcessError as err:
        detail = (err.stderr or err.stdout or "").strip()
        warn(f"command failed: {' '.join(args)}{': ' + detail if detail else ''}")
    return ""
