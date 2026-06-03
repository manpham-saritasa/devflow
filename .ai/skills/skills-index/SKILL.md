---
name: skills-index
version: 0.1.0
description: Scan all skill directories and generate skills-index.md with name, path, triggers, and description for LLM discovery.
triggers:
  - "skills-index"
  - "scan skills"
  - "update skills index"
---

## When to use

- After creating, renaming, or deleting any skill
- After updating a skill's frontmatter (name, triggers, description)
- When skills-index.md is out of date

## Workflow

### Step 1: Run the scanner

```bash
python .ai/skills/skills-index/scripts/scan.py
```

This scans:
- `.ai/plugins/` — all plugin skills (devflow, jiraflow, githubflow, refflow)
- `.ai/skills/` — standalone skills (md-view, grill-me, caveman, etc.)
- `.agents/skills/` — agent skills (review-design, review-md, quick-refactor)
- `.local/skills/` — personal skills (jira-log)

### Step 2: Verify

Read `skills-index.md` and confirm:
- All skills found
- No duplicates
- Paths match actual directories

### Step 3: Report

Show summary: "Scanned [N] skills across [M] directories. Updated skills-index.md."

## Rules

- Run this skill after any skill rename, creation, or deletion
- The generated file is `.ai/skills-index.md` — LLMs read this at startup
