# Jiraflow Plugin — Shared Configuration

## Paths

| Variable | Value | Description |
|----------|-------|-------------|
| `PLUGIN_ROOT` | `.ai/plugins/jiraflow` | Plugin root (repo-relative) |

## Auth

All skills read credentials from `.env.local` (preferred) or `.env` in the repo root:

- `JIRA_COMPANY_DOMAIN` — Atlassian subdomain (e.g., `saritasa`)
- `JIRA_EMAIL` — Atlassian account email
- `JIRA_API_TOKEN` — Atlassian API token
- `JIRA_PROJECT_KEY` — default project key (e.g., `PROJ`)
- `TEMPO_API_TOKEN` — Tempo API token (for jira-log, future)

Scripts load env by calling `load_env()` — defined in each skill's `main.py`.
