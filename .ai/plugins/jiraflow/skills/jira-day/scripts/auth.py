import base64
import os
import re
from typing import Any

import yaml
from common import PROJECT_KEY_RE, run_command


def load_env(root: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for fname in [".env.jira", ".env"]:
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
        raise SystemExit("Missing JIRA credentials in .env.jira or .env")
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    return domain, email, auth


def validate_project_key(project: str) -> None:
    if not PROJECT_KEY_RE.match(project):
        raise SystemExit(
            f"Invalid project key: {project}. Expected format like RMASUP or PROJ."
        )
