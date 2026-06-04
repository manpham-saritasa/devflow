import os
import re
from typing import Any

import yaml
from common import DEFAULT_STAGE_GROUPS, ROLES, warn

DONE_STATUSES = 'Completed,Done,Closed,Resolved,"On Production","On Staging"'


def read_yaml(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}


def ensure_local_config(
    config_path: str,
    config_template_path: str,
    local_dir: str,
    reset_role: bool = False,
) -> dict[str, Any]:
    data = read_yaml(config_path)
    if data and not reset_role:
        return data
    template = read_yaml(config_template_path)
    os.makedirs(local_dir, exist_ok=True)
    print("First-time jira-day setup")
    role = (
        input("Role [dev/qa/tm/pm/mixed] (default: mixed): ").strip().lower() or "mixed"
    )
    if role not in ROLES:
        role = "mixed"
    pr_answer = (
        input("Do you do PR activity as part of your work? [y/N]: ").strip().lower()
    )
    template["role"] = role
    template["check_pr_activity"] = pr_answer in {"y", "yes"}
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(template, f, sort_keys=False, allow_unicode=True)
    return template


def load_stage_groups(root: str) -> dict[str, list[str]]:
    path = os.path.join(root, ".ai", "plugins", "jiraflow", "config.md")
    if not os.path.exists(path):
        return DEFAULT_STAGE_GROUPS.copy()
    text = open(path, encoding="utf-8").read()
    match = re.search(r"## Stage groups.*?```yaml\n(.*?)```", text, re.S)
    if not match:
        return DEFAULT_STAGE_GROUPS.copy()
    try:
        parsed = yaml.safe_load(match.group(1)) or {}
        groups = parsed.get("stage_groups") or {}
        out = DEFAULT_STAGE_GROUPS.copy()
        if isinstance(groups, dict):
            for key, values in groups.items():
                if isinstance(values, list):
                    out[key] = [str(v) for v in values]
        return out
    except Exception as err:
        warn(f"failed to parse stage groups from jiraflow config: {err}")
        return DEFAULT_STAGE_GROUPS.copy()


def merge_stage_groups(
    base: dict[str, list[str]], override: Any
) -> dict[str, list[str]]:
    out = {k: list(v) for k, v in base.items()}
    if isinstance(override, dict):
        for key, values in override.items():
            if isinstance(values, list):
                out[key] = [str(v) for v in values]
    return out


def load_favorite_projects(root: str) -> list[str]:
    path = os.path.join(root, ".local", "jiraflow", "config.yaml")
    if not os.path.exists(path):
        return []
    try:
        data = yaml.safe_load(open(path, encoding="utf-8")) or {}
        projects = data.get("favorite_projects") or []
        return [str(p) for p in projects if p]
    except Exception:
        return []
