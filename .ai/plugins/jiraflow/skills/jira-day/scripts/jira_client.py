from typing import Any

from common import HTTP_TIMEOUT_SECONDS
from settings import DONE_STATUSES, jira_get, jira_post


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
