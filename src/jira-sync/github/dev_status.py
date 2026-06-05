"""GitHub PR dev-status fetcher for Jira issues.

Fetches linked GitHub PRs from the Jira dev-status API.
"""

import re

import requests
from jira.config import AUTH, HEADERS, HTTP_TIMEOUT_SECONDS, JIRA_URL


def fetch_issue_dev_status(issue_id: int) -> list[dict[str, str]]:
    """Fetch linked GitHub PRs from Jira dev-status integration.

    Returns list of {"repo", "number", "url", "title", "state"}.
    """
    url = f"{JIRA_URL}/rest/dev-status/1.0/issue/detail"
    params = {
        "issueId": str(issue_id),
        "applicationType": "GitHub",
        "dataType": "pullrequest",
    }
    try:
        resp = requests.get(
            url, params=params, auth=AUTH, headers=HEADERS, timeout=HTTP_TIMEOUT_SECONDS
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"  [dev-status] ERROR: {e}")
        return []

    details = data.get("detail", [])
    if not details:
        return []

    prs: list[dict[str, str]] = []
    for detail in details:
        for pr in detail.get("pullRequests", []):
            pr_url = (pr.get("url") or "").strip()
            if not pr_url:
                continue
            # url format: https://github.com/owner/repo/pull/123
            match = re.match(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", pr_url)
            if not match:
                continue
            repo = match.group(1)
            number = match.group(2)
            prs.append(
                {
                    "repo": repo,
                    "number": number,
                    "url": pr_url,
                    "title": (pr.get("name") or ""),
                    "state": (pr.get("status") or "UNKNOWN"),
                }
            )
    return prs
