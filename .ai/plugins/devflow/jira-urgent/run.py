"""Run jira-urgent check and save to file. Called by Windows Task Scheduler daily at 8am."""

import base64
import json
import os
import sys
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)


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
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"')
    return env


def load_ignored():
    ignored = set()
    path = os.path.join(ROOT, ".local", "jira", "ignored-comments.txt")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored.add(line)
    return ignored


def extract_text(node):
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if node.get("type") == "text":
            return node.get("text", "")
        if node.get("type") == "mention":
            return "@" + node.get("attrs", {}).get("text", "")
        if node.get("type") == "hardBreak":
            return "\n"
        return "".join(extract_text(c) for c in node.get("content", []))
    if isinstance(node, list):
        return "".join(extract_text(i) for i in node)
    return ""


def has_mention(node, account_id):
    """Check if an Atlassian Document Format body contains a mention of account_id."""
    if isinstance(node, dict):
        if (
            node.get("type") == "mention"
            and node.get("attrs", {}).get("id") == account_id
        ):
            return True
        return any(has_mention(v, account_id) for v in node.values())
    if isinstance(node, list):
        return any(has_mention(i, account_id) for i in node)
    return False


def main():
    env = load_env()
    domain = env.get("JIRA_COMPANY_DOMAIN", "")
    email = env.get("JIRA_EMAIL", "")
    token = env.get("JIRA_API_TOKEN", "")
    project = env.get("JIRA_PROJECT_KEY", "RMASUP")

    if not all([domain, email, token]):
        print("Missing JIRA credentials in .env.local")
        sys.exit(1)

    auth = base64.b64encode(f"{email}:{token}".encode()).decode()

    # Get account ID
    req = urllib.request.Request(f"https://{domain}.atlassian.net/rest/api/3/myself")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req) as resp:
        account_id = json.loads(resp.read())["accountId"]

    ignored = load_ignored()

    urgent = []
    seen = set()

    queries = [
        f'project={project} AND sprint in openSprints() AND (assignee=currentUser() OR reporter=currentUser() OR issue in watchedIssues()) AND status not in (Completed,Done,Closed,Resolved,"On Production","On Staging") ORDER BY priority DESC, updated DESC',
    ]

    for jql in queries:
        body = json.dumps(
            {
                "jql": jql,
                "maxResults": 25,
                "fields": [
                    "summary",
                    "status",
                    "priority",
                    "comment",
                    "assignee",
                    "updated",
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
            data = json.loads(resp.read())
            for issue in data.get("issues", []):
                key = issue["key"]
                if key in seen:
                    continue
                seen.add(key)
                f = issue["fields"]
                comments = f.get("comment", {}).get("comments", [])
                uc = None
                for c in reversed(comments):
                    if c["author"].get("accountId", "") == account_id:
                        break
                    bt = extract_text(c.get("body", ""))
                    if has_mention(c.get("body", ""), account_id) or "?" in bt:
                        uc = c
                        break
                if uc:
                    cid = str(uc["id"])
                    if cid in ignored:
                        continue
                    bt = extract_text(uc.get("body", ""))
                    tag = (
                        "verify"
                        if any(
                            kw in bt.lower()
                            for kw in [
                                "fixed",
                                "resolved",
                                "please have a look",
                                "please verify",
                                "please check",
                                "ready for review",
                                "worked on dev",
                            ]
                        )
                        else "at_mention"
                    )
                    urgent.append(
                        {
                            "key": key,
                            "summary": f["summary"],
                            "status": f["status"]["name"],
                            "priority": f.get("priority", {}).get("name", "?"),
                            "author": uc["author"]["displayName"],
                            "comment_id": cid,
                            "body": bt[:200],
                            "tag": tag,
                        }
                    )

    # Sort
    stage_order = {
        "Blocked": 0,
        "On Hold": 0,
        "Ready for Development": 1,
        "In Progress": 1,
        "Code Review": 1,
        "TM Review": 2,
        "In Review": 2,
    }
    p_order = {"Highest": 0, "High": 1, "Medium": 2, "Low": 3, "Lowest": 4}
    urgent.sort(
        key=lambda x: (
            stage_order.get(x["status"], 99),
            0 if x["tag"] == "at_mention" else 1,
            p_order.get(x["priority"], 5),
        )
    )

    today = datetime.now().strftime("%Y-%m-%d")
    out = [f"# Jira - Urgent Tasks: {project} ({today})\n"]
    out.append(f"**{len(urgent)} urgent** ({len(ignored)} ignored)\n")

    if not urgent:
        out.append("No urgent items — team is not blocked on you.")
    else:
        for item in urgent:
            key = item["key"]
            cid = item["comment_id"]
            out.append(
                f"- [{key}](https://{domain}.atlassian.net/browse/{key}?focusedCommentId={cid}) — {item['status']} | {item['priority']} | {item['author']} ({item['tag']})"
            )

    output_dir = os.path.join(ROOT, ".local", "jira")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"urgent-{today}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print(f"Saved: {path} ({len(urgent)} items)")


if __name__ == "__main__":
    main()
