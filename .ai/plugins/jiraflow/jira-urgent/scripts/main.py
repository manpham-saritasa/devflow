"""Run jira-urgent check and save to file. Called by Windows Task Scheduler daily at 8am."""

import base64
import json
import os
import sys
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
    )
)

VERIFY_KEYWORDS = [
    "fixed",
    "resolved",
    "please have a look",
    "please verify",
    "please check",
    "ready for review",
    "worked on dev",
]

STAGE_ORDER = {
    "Blocked": 0,
    "On Hold": 0,
    "Ready for Development": 1,
    "In Progress": 1,
    "Code Review": 1,
    "TM Review": 2,
    "In Review": 2,
}

PRIORITY_ORDER = {"Highest": 0, "High": 1, "Medium": 2, "Low": 3, "Lowest": 4}


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
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ignored-comments.txt"
    )
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


def get_account_id(domain, auth):
    req = urllib.request.Request(f"https://{domain}.atlassian.net/rest/api/3/myself")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["accountId"]


def fetch_issues(domain, auth, project):
    jql = (
        f"project={project} AND sprint in openSprints() AND "
        f"(assignee=currentUser() OR reporter=currentUser() OR issue in watchedIssues()) AND "
        f'status not in (Completed,Done,Closed,Resolved,"On Production","On Staging") '
        f"ORDER BY priority DESC, updated DESC"
    )
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
        return json.loads(resp.read()).get("issues", [])


def find_urgent_comment(comments, account_id, ignored_ids):
    for comment in reversed(comments):
        if comment["author"].get("accountId", "") == account_id:
            return None
        body_text = extract_text(comment.get("body", ""))
        if has_mention(comment.get("body", ""), account_id) or "?" in body_text:
            comment_id = str(comment["id"])
            if comment_id in ignored_ids:
                return None
            return {
                "id": comment_id,
                "author": comment["author"]["displayName"],
                "body": body_text,
            }
    return None


def classify_intent(body_text):
    if any(kw in body_text.lower() for kw in VERIFY_KEYWORDS):
        return "verify"
    return "at_mention"


def sort_urgent(items):
    items.sort(
        key=lambda item: (
            STAGE_ORDER.get(item["status"], 99),
            0 if item["tag"] == "at_mention" else 1,
            PRIORITY_ORDER.get(item["priority"], 5),
        )
    )


def build_output(items, ignored_count, project, domain, today):
    out = [f"# Jira - Urgent Tasks: {project} ({today})\n"]
    out.append(f"**{len(items)} urgent** ({ignored_count} ignored)\n")

    if not items:
        out.append("No urgent items — team is not blocked on you.")
    else:
        for item in items:
            key = item["key"]
            comment_id = item["comment_id"]
            out.append(
                f"- [{key}](https://{domain}.atlassian.net/browse/{key}"
                f"?focusedCommentId={comment_id}) — "
                f"{item['status']} | {item['priority']} | {item['author']} ({item['tag']})"
            )
    return "\n".join(out)


def main():
    env = load_env()
    domain = env.get("JIRA_COMPANY_DOMAIN", "")
    email = env.get("JIRA_EMAIL", "")
    token = env.get("JIRA_API_TOKEN", "")
    project = env.get("JIRA_PROJECT_KEY", "PROJ")
    # Override with positional arg (e.g., jurgent COAPS)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        project = sys.argv[1].upper()

    if not all([domain, email, token]):
        print("Missing JIRA credentials in .env.local")
        sys.exit(1)

    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    account_id = get_account_id(domain, auth)
    ignored_ids = load_ignored()

    issues = fetch_issues(domain, auth, project)
    urgent = []

    for issue in issues:
        key = issue["key"]
        fields = issue["fields"]
        comments = fields.get("comment", {}).get("comments", [])
        urgent_comment = find_urgent_comment(comments, account_id, ignored_ids)
        if urgent_comment is None:
            continue

        body_text = urgent_comment["body"]
        tag = classify_intent(body_text)
        urgent.append(
            {
                "key": key,
                "summary": fields["summary"],
                "status": fields["status"]["name"],
                "priority": fields.get("priority", {}).get("name", "?"),
                "author": urgent_comment["author"],
                "comment_id": urgent_comment["id"],
                "body": body_text[:200],
                "tag": tag,
            }
        )

    sort_urgent(urgent)

    today = datetime.now().strftime("%Y-%m-%d")
    output = build_output(urgent, len(ignored_ids), project, domain, today)
    print(output)
    print(f"\n{len(urgent)} urgent, {len(ignored_ids)} ignored")


if __name__ == "__main__":
    main()
