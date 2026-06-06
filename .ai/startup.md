# AI Session Startup

Read `.ai/README.md` for full deployment guide and folder structure.

---

## Start of every session

| Step | Action |
|---|---|
| 1 | If `.local/memory.md` exists, read it and follow for the whole session |
| 2 | If `.local/session-rules.md` exists, read and follow session tracking rules |
| 3 | If `.local/sessions/last-summary.md` exists, read it as previous-session context |
| 4 | If `.local/sessions/corrections.md` exists, read it — avoid repeating past mistakes |
| 5 | Scan `.ai/skills-index.md` for available skills (do not load fully — only scan trigger names) |

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
| Coding (implement, fix, refactor) | `.ai/rules/coding-rules.md` |

If multiple apply, read all matching files before starting.

---

## Priority order

| Priority | Source |
|---|---|
| 1 | User instruction |
| 2 | `.local/memory.md` |
| 3 | Chosen agent from `.ai/agents/` |
| 4 | Chosen skill from `.ai/skills/` or `.ai/plugins/` |
| 5 | On-demand rules from `.ai/rules/` |
| 6 | `.ai/rules/core.md` (core rules) |
| 7 | Default AI behavior |
