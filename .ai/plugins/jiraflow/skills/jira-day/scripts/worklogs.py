import os
import re
from collections import defaultdict
from datetime import datetime

JIRA_LOG_RELATIVE = [".local", "skills", "jira-log", "main.py"]


def get_today_worklogs(root: str) -> dict[str, int]:
    jira_log_script = os.path.join(root, *JIRA_LOG_RELATIVE)
    if not os.path.exists(jira_log_script):
        return {}
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(root, ".local", "jira", "logs", f"{date_str}.md")
    if not os.path.exists(path):
        return {}

    totals: dict[str, int] = defaultdict(int)
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if (
            not line.startswith("|")
            or line.startswith("| Task")
            or line.startswith("| ---")
        ):
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 4:
            continue
        match = re.match(r"\[(.+?)\]\(", parts[0])
        if not match:
            continue
        seconds = 0
        for amt, unit in re.findall(r"(\d+)\s*([hm])", parts[2]):
            seconds += int(amt) * (3600 if unit == "h" else 60)
        totals[match.group(1)] += seconds
    return dict(totals)
