# AI Session Startup

Read `.ai/README.md` for full deployment guide and folder structure.

---

## Start of every session

**Always read `.ai/rules/core.md` before anything else — framework rules.**

| Step | Action | If Missing — Tell User |
|---|---|---|
| 1 | If `.local/memory.md` exists, read it and follow for the whole session | "No personal memory set up. Copy `.ai/rules/memory.md.template` to `.local/memory.md` to customize shortcuts and behavior." |
| 2 | If `.local/session-rules.md` exists, read and follow session tracking rules | "No session tracking rules set up. Copy `.ai/rules/session-rules.md.template` to `.local/session-rules.md`." |
| 3 | If `.local/sessions/last-summary.md` exists, read it as previous-session context | "No previous session summary found — starting fresh." |
| 4 | If `.local/sessions/corrections.md` exists, read it — avoid repeating past mistakes | "No corrections history found." |
| 5 | Scan `.ai/skills-index.md` for available skills (do not load fully — only scan trigger names) | "No skills index found. Run `.ai/skills/skills-index/scan.py` to generate it." |

> ⚠️ **Tool limitation:** `find_path` skips gitignored directories (`.local/`). After running the checks above, always verify `.local/` results with `list_directory` — do not trust `find_path` for `.local` files.

If session is long, task changes, or context is fuzzy, re-read it.

---

## When user says use an agent

| Step | Action |
|---|---|
| 1 | Go to `.ai/agents/` |
| 2 | Find best agent for the task |
| 3 | Read that agent file |
| 4 | Do task using that agent's job and limits |

If many agents fit, pick best match.
If no agent fits, say no good agent found, then continue with memory and rules only.

---

## When task needs a skill

| Step | Action |
|---|---|
| 1 | Go to `.ai/skills/` or `.ai/plugins/` |
| 2 | Find best skill for the task |
| 3 | Read that skill file |
| 4 | Use that skill alongside memory and rules |

If many skills fit, pick best match.
If no skill fits, say no good skill found, then continue with memory and rules only.

---

## On-demand rules — load by task type

Before starting a task, check if a matching rule file exists and read it:

| Task type | Read this |
|---|---|
| Coding (implement, fix, refactor) | `.ai/rules/coding.md` |

If multiple apply, read all matching files before starting.

---

## Priority order

| Priority | Source |
|---|---|
| 1 | User instruction |
| 2 | `.ai/rules/core.md` (core rules) |
| 3 | `.local/memory.md` |
| 4 | Chosen agent from `.ai/agents/` |
| 5 | Chosen skill from `.ai/skills/` or `.ai/plugins/` |
| 6 | On-demand rules from `.ai/rules/` |
| 7 | Default AI behavior |
