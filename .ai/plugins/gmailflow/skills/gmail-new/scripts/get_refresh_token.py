"""Local OAuth helper for generating a Gmail refresh token."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
REQUIRED_VARS = ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]


def load_env(env_path: Path) -> dict[str, str]:
    """Load OAuth client values from the repo-local Gmail env file."""
    data: dict[str, str] = {}
    if not env_path.exists():
        return data
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def build_missing_env_payload(
    env_path: Path, repo_root: Path, missing: list[str]
) -> dict[str, object]:
    """Build a consistent error payload for incomplete OAuth client setup."""
    return {
        "ok": False,
        "message": "Missing required OAuth client variables.",
        "env_file": str(env_path.relative_to(repo_root)),
        "missing": missing,
    }


def build_client_config(env: dict[str, str]) -> dict[str, dict[str, object]]:
    """Build the installed-app OAuth client configuration for Google login."""
    return {
        "installed": {
            "client_id": env["GOOGLE_CLIENT_ID"],
            "client_secret": env["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def build_oauth_flow(client_config: dict[str, dict[str, object]]):
    """Create the Google installed-app OAuth flow only when needed at runtime."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    return InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI args for local-server or pasted redirect URL OAuth flows."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--redirect-url", default="")
    return parser


def extract_auth_code(redirect_url: str) -> str:
    """Extract the Google OAuth authorization code from a pasted redirect URL."""
    if not redirect_url.strip():
        return ""
    query = parse_qs(urlparse(redirect_url).query)
    values = query.get("code", [])
    return values[0] if values else ""


def run_flow(flow, redirect_url: str):
    """Complete OAuth either via local server or a pasted redirect URL."""
    auth_code = extract_auth_code(redirect_url)
    if auth_code:
        flow.redirect_uri = "http://localhost"
        flow.fetch_token(code=auth_code)
        return flow.credentials
    return flow.run_local_server(port=0, prompt="consent", access_type="offline")


def main() -> int:
    """Run the local OAuth flow and print the refresh token payload."""
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[6]
    env_path = repo_root / ".env.gmail"
    env = load_env(env_path)

    missing = [key for key in REQUIRED_VARS if not env.get(key)]
    if missing:
        payload = build_missing_env_payload(env_path, repo_root, missing)
        print(json.dumps(payload, indent=2))
        return 1

    client_config = build_client_config(env)
    flow = build_oauth_flow(client_config)
    creds = run_flow(flow, args.redirect_url)
    payload = {
        "ok": True,
        "env_file": str(env_path.relative_to(repo_root)),
        "gmail_account": getattr(creds, "account", None),
        "scopes": list(creds.scopes or []),
        "refresh_token": creds.refresh_token,
        "note": "Copy refresh_token into .env.gmail as GOOGLE_REFRESH_TOKEN",
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
