---
name: jira-move
description: Transition a Jira issue to a target status. Reads per-project .config file for known transitions, discovers IDs on first run.
triggers:
  - "jira-move"
  - "jmove"
---

## Usage

```
jmove PROJ-123                  → auto-detect next step and move
jmove PROJ-1500 ready           → move to Ready For Development
jmove PROJ-2134 review          → move to Code Review
jmove PROJ-2113 qa              → move to Ready for QA
jmove PROJ-1000 --discover      → discover all transitions, save to config
```

---

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Move issue to target status |
| `--discover` | Discover all available transitions for this issue and save to config. Do not execute. |

---

## Paths

- `PROJECT_KEY` — extracted from Jira issue key (e.g., `PROJ-1105` → `PROJ`)
- `CONFIG` — `./[PROJECT_KEY].config` (skill-relative)
- `TEMPLATE` — `./PROJECT-KEY.config.template` — copy and rename for new projects

---

## Workflow

### Step 1: Parse Input

- `KEY` — Jira issue key
- `MILESTONE` — one of: `ready`, `review`, `qa`. If omitted, auto-detect next step.
- `--discover` — optional flag

### Step 2: Load Credentials

Read `.env.local` (preferred) or `.env` from repo root. Extract:
- `JIRA_DOMAIN` or `JIRA_COMPANY_DOMAIN` — the Atlassian subdomain (e.g., `saritasa`)
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

Do not use `source` — read the file and parse `KEY=VALUE` lines directly.

If missing: stop — "❌ Jira credentials not found in .env.local or .env."

> When called from pipeline skills (dev-start/dev-ship): skip silently instead of stopping.

### Step 3: Load Config

Extract `PROJECT_KEY` from the issue key (everything before the `-`).

Check for `./[PROJECT_KEY].config`. If not found: stop — "❌ No config found for [PROJECT_KEY]. Copy `PROJECT-KEY.config.template` → `[PROJECT_KEY].config` and fill in your project's status names."

No fallback. Every project must have its own config.

> When called from pipeline skills: skip silently instead of stopping.

### If --discover

Fetch all available transitions from this issue, match against all 3 config prefixes, save discovered IDs, and stop:

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://${JIRA_COMPANY_DOMAIN}.atlassian.net/rest/api/3/issue/${KEY}/transitions" \
  | jq '.transitions[] | {id, name, to: .to.name}'
```

For each milestone prefix (`READY_FOR_DEV`, `IN_PROGRESS`, `CODE_REVIEW`, `READY_FOR_QA`), match the config's `[PREFIX]_NAME` against available transitions (case-insensitive). If found, write the ID to config. Report which were found and which need discovery from a different issue state.

Stop here — do not execute any transition.

### If not --discover:

### Step 4: Determine Target

**If no milestone given:** fetch current status first, then auto-detect next step:

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://${JIRA_COMPANY_DOMAIN}.atlassian.net/rest/api/3/issue/${KEY}?fields=status" \
  | jq -r '.fields.status.name'
```

| Current status | Next milestone |
|----------------|---------------|
| Backlog | `ready` |
| Ready For Development | `in-progress` |
| In Progress | `review` |
| Code Review | `qa` |
| Ready for QA | `done` — dev pipeline complete |

Match current status (case-insensitive). If no match: "⚠️  Current status [STATUS] not in dev flow. Use `ready`, `review`, or `qa`." Skip.

If `done`: "✅ Dev pipeline complete for [KEY]. Hand off to QA." Stop.

**Otherwise:** map milestone to config prefix:

| Milestone | Prefix | Example target |
|-----------|--------|----------------|
| `ready` | `READY_FOR_DEV` | "Ready For Development" |
| `in-progress` | `IN_PROGRESS` | "In Progress" |
| `review` | `CODE_REVIEW` | "Code Review" |
| `qa` | `READY_FOR_QA` | "Ready for QA" |

Read `[PREFIX]_NAME` from config. Use it as the target status name.

### Step 5: Check Current Status

> If status was already fetched in Step 4 (auto-detect mode), skip the API call — reuse cached result.

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://${JIRA_COMPANY_DOMAIN}.atlassian.net/rest/api/3/issue/${KEY}?fields=status" \
  | jq -r '.fields.status.name'
```

If already at target status: skip — "✅ Jira [KEY] already at [TARGET]."

### Step 6: Find Transition

**If config has `[PREFIX]_ID` with a value:** use it directly. No API call needed.

**If config has no ID:** call the transitions API:

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "https://${JIRA_COMPANY_DOMAIN}.atlassian.net/rest/api/3/issue/${KEY}/transitions" \
  | jq '.transitions[] | {id, name, to: .to.name}'
```

Match the target name (case-insensitive) from the available transitions. If no match found: "⚠️  Transition to [TARGET] not available from current status. Run `jmove [KEY] --discover` to see available transitions." Skip.

### Step 7: Execute Transition

```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"transition\": {\"id\": \"$TRANSITION_ID\"}}" \
  "https://${JIRA_COMPANY_DOMAIN}.atlassian.net/rest/api/3/issue/${KEY}/transitions"
```

If the API returns validation errors (e.g., missing required fields): report the error — "⚠️  Jira requires: [field names]." Do not retry. The user must fill required fields in Jira first.

### Step 8: Save Discovery

If the transition ID was discovered at runtime (not in config), write it to `CONFIG`:
```
READY_FOR_DEV_ID=221
```

### Step 9: Report

```
✅ Jira [KEY] → [TARGET_STATUS]
```
Or if failed:
```
⚠️  Jira transition skipped: [reason]
```

**Non-blocking:** never fail the calling skill. Log warning and continue.
