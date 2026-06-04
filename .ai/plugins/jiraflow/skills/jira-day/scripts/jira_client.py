import json
import urllib.request
from typing import Any

from common import HTTP_TIMEOUT_SECONDS
from settings import DONE_STATUSES


def jira_get(url: str, auth: str) -> dict[str, Any]:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read())


def jira_post(url: str, auth: str, body: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(url, data=json.dumps(body).encode())
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read())


def fetch_account(domain: str, auth: str) -> dict[str, Any]:
    return jira_get(f"https://{domain}.atlassian.net/rest/api/3/myself", auth)


def fetch_issues(
    domain: str, auth: str, project: str, hours: int
) -> list[dict[str, Any]]:
    jql = (
        f"project={project} AND updated >= -{hours}h AND status not in ({DONE_STATUSES}) "
        f"ORDER BY updated DESC"
    )
    body = {
        "jql": jql,
        "maxResults": 100,
        "fields": [
            "summary",
            "status",
            "priority",
            "comment",
            "assignee",
            "updated",
            "worklog",
        ],
    }
    data = jira_post(
        f"https://{domain}.atlassian.net/rest/api/3/search/jql", auth, body
    )
    return data.get("issues", [])


def fetch_changelog(domain: str, auth: str, key: str) -> list[dict[str, Any]]:
    data = jira_get(
        f"https://{domain}.atlassian.net/rest/api/3/issue/{key}/changelog?maxResults=100",
        auth,
    )
    return data.get("values", [])
