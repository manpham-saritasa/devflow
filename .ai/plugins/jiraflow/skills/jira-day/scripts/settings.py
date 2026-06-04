import base64
import json
import os
import re
import urllib.request
from typing import Any

import yaml
from common import (
    DEFAULT_STAGE_GROUPS,
    HTTP_TIMEOUT_SECONDS,
    PROJECT_KEY_RE,
    ROLES,
    run_command,
    warn,
)

DONE_STATUSES = 'Completed,Done,Closed,Resolved,"On Production","On Staging"'


def read_yaml(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}


def load_env(root: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for fname in [".env.local", ".env"]:
        path = os.path.join(root, fname)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip().strip('"')
    return env


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


def detect_identity(
    config: dict[str, Any], env: dict[str, str], root: str
) -> dict[str, str]:
    identity = dict(config.get("identity") or {})
    if not identity.get("jira_email"):
        identity["jira_email"] = env.get("JIRA_EMAIL", "")
    if not identity.get("git_email"):
        identity["git_email"] = run_command(["git", "config", "user.email"], root)
    if not identity.get("github_username"):
        status = run_command(["gh", "auth", "status"], root)
        match = re.search(r"Logged in to github.com account (\S+)", status)
        if match:
            identity["github_username"] = match.group(1)
    return identity


def persist_identity_if_changed(
    config: dict[str, Any], identity: dict[str, str], config_path: str, local_dir: str
) -> None:
    if identity == (config.get("identity") or {}):
        return
    config["identity"] = identity
    os.makedirs(local_dir, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)


def jira_auth(env: dict[str, str], config: dict[str, Any]) -> tuple[str, str, str]:
    identity = config.get("identity") or {}
    domain = env.get("JIRA_COMPANY_DOMAIN", "")
    email = identity.get("jira_email") or env.get("JIRA_EMAIL", "")
    token = env.get("JIRA_API_TOKEN", "")
    if not all([domain, email, token]):
        raise SystemExit("Missing JIRA credentials in .env.local or .env")
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    return domain, email, auth


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


def validate_project_key(project: str) -> None:
    if not PROJECT_KEY_RE.match(project):
        raise SystemExit(
            f"Invalid project key: {project}. Expected format like RMASUP or PROJ."
        )
