"""List assigned Jira tasks by status group. Called manually or via cron."""

import base64
import json
import os
import sys
import urllib.request
from datetime import datetime

# Handle non-breaking hyphens and other Unicode in JIRA task descriptions
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
    )
)

ONGOING_STATES = {
    "In Progress",
    "Code Review",
    "TM Review",
    "In Review",
    "Blocked",
    "On Hold",
}

READY_STATES = {
    "Ready for Development",
    "Open",
    "To Do",
    "Reopened",
}

PRIORITY_ORDER = {"Highest": 0, "High": 1, "Medium": 2, "Low": 3, "Lowest": 4}


def extract_text(node):
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if node.get("type") == "text":
            return node.get("text", "")
        if node.get("type") == "mention":
            return "@" + node.get("attrs", {}).get("text", "")
        if node.get("type") == "hardBreak":
            return " "
        content = node.get("content", [])
        if content:
            parts = [extract_text(c) for c in content]
            return " ".join(p for p in parts if p)
        return ""
    if isinstance(node, list):
        parts = [extract_text(i) for i in node]
        return " ".join(p for p in parts if p)
    return ""


def load_env():
    env = {}
    for fname in [".env.local", ".env"]:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip().strip('"')
    return env


def load_ignored():
    ignored = set()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore-tasks.txt")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored.add(line)
    return ignored


def fetch_tasks(domain, auth, project):
    jql = (
        f"project={project} AND assignee=currentUser() AND "
        f'status not in (Completed,Done,Closed,Resolved,"On Production","On Staging",Backlog) '
        f"ORDER BY priority DESC, updated DESC"
    )
    body = json.dumps(
        {
            "jql": jql,
            "maxResults": 50,
            "fields": [
                "summary",
                "status",
                "priority",
                "issuetype",
                "updated",
                "description",
            ],
        }
    ).encode()
    req = urllib.request.Request(
        f"https://{domain}.atlassian.net/rest/api/3/search/jql", data=body
    )
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read()).get("issues", [])


def group_tasks(issues, ignored_ids):
    ongoing = []
    ready = []
    for issue in issues:
        key = issue["key"]
        if key in ignored_ids:
            continue
        fields = issue["fields"]
        status = fields["status"]["name"]
        description_raw = fields.get("description") or ""
        description_text = (
            extract_text(description_raw).strip() if description_raw else ""
        )
        if len(description_text) > 300:
            description_text = description_text[:300] + "..."
        item = {
            "key": key,
            "summary": fields["summary"],
            "description": description_text,
            "status": status,
            "priority": fields.get("priority", {}).get("name", "?"),
            "url": f"https://saritasa.atlassian.net/browse/{key}",
        }
        if status in ONGOING_STATES:
            ongoing.append(item)
        elif status in READY_STATES:
            ready.append(item)
        else:
            ongoing.append(item)

    sort_key = lambda item: PRIORITY_ORDER.get(item["priority"], 5)
    ongoing.sort(key=sort_key)
    ready.sort(key=sort_key)
    return ongoing, ready


def build_output(ongoing, ready, ignored_count, project, today):
    out = [f"# Jira - My Tasks: {project} ({today})\n"]
    total = len(ongoing) + len(ready)
    out.append(
        f"**{total} pending** ({len(ongoing)} on-going, {len(ready)} ready, {ignored_count} ignored)\n"
    )

    if ongoing:
        out.append(f"## On-Going ({len(ongoing)})\n")
        for i, item in enumerate(ongoing, 1):
            out.append(
                f"### {i}. [{item['key']}]({item['url']}) — {item['priority']} | {item['status']}"
            )
            out.append(f"**{item['summary']}:**")
            if item.get("description"):
                out.append("")
                out.append(item["description"])
            out.append("")

    if ready:
        out.append(f"\n## Ready for Development ({len(ready)})\n")
        for i, item in enumerate(ready, 1):
            out.append(f"### {i}. [{item['key']}]({item['url']}) — {item['priority']}")
            out.append(f"**{item['summary']}:**")
            if item.get("description"):
                out.append("")
                out.append(item["description"])
            out.append("")

    if not ongoing and not ready:
        out.append("No pending tasks.")

    return "\n".join(out)


def main():
    show_pending = "--pending" in sys.argv
    show_ready = "--ready" in sys.argv
    show_review = "--review" in sys.argv

    env = load_env()
    domain = env.get("JIRA_COMPANY_DOMAIN", "")
    email = env.get("JIRA_EMAIL", "")
    token = env.get("JIRA_API_TOKEN", "")
    project = env.get("JIRA_PROJECT_KEY", "PROJ")
    # Positional arg: KEY (non-flag) overrides project
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            project = arg.upper()
            break

    if not all([domain, email, token]):
        print("Missing JIRA credentials in .env.local")
        sys.exit(1)

    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    issues = fetch_tasks(domain, auth, project)
    ignored_ids = load_ignored()
    ongoing, ready = group_tasks(issues, ignored_ids)

    if show_pending:
        ready = []
    elif show_ready:
        ongoing = []
    elif show_review:
        ongoing = [t for t in ongoing if t["status"] in ("In Review", "TM Review")]
        ready = []

    today = datetime.now().strftime("%Y-%m-%d")
    output = build_output(ongoing, ready, len(ignored_ids), project, today)
    print(output)

    total = len(ongoing) + len(ready)
    print(
        f"\n{total} tasks ({len(ongoing)} on-going, {len(ready)} ready, {len(ignored_ids)} ignored)"
    )


if __name__ == "__main__":
    main()
