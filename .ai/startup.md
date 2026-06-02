# AI Session Startup

Orchestration file for this repository.
Read this before starting any work if available.

---

## Supported AI tools

This file is loaded via `AGENTS.md` which is auto-read by:

| Tool | Auto-reads `AGENTS.md` |
|---|---|
| OpenAI Codex CLI | ✅ |
| OpenCode | ✅ |
| GitHub Copilot (coding agent) | ✅ |
| Claude Code | ✅ via `CLAUDE.md` symlink |
| Gemini CLI | ✅ via `GEMINI.md` symlink |
| Windsurf | ✅ via `.windsurfrules` symlink |
| Codeium | ✅ via `.codeiumrules` symlink |
| Aider | ✅ via `CONVENTIONS.md` symlink |
| Zed | ✅ via `.rules` symlink |
| JetBrains AI Assistant | ✅️ via `.rules` symlink |
| Cursor | ✅ via `.cursor/rules/main.mdc` — points to `AGENTS.md` |

> Edit only `AGENTS.md`. Run `sync.sh` or `sync.ps1` to propagate to all tool-specific files.

---

## Start of every session

| Step | Action |
|---|---|
| 1 | If `.local/memory.md` exists, read it and follow for the whole session |
| 2 | If `.local/session-rules.md` exists, read and follow session tracking rules |
| 3 | If `skills-index.md` exists, read it for full skill list |
| 4 | Read `.ai/skills/matt-pocock/caveman/SKILL.md` and use caveman mode when talking to user directly |

If session is long, task changes, or context is fuzzy, re-read it.

---

## Set up your personal workspace

Copy and customize the templates in `.ai/rules/`:

```bash
cp .ai/rules/memory.md.template .local/memory.md
cp .ai/rules/session-rules.md.template .local/session-rules.md
```

| File | Purpose |
|------|---------|
| `memory.md` | Your shortcuts (`cush`, `ship`, `creport`), communication preferences, and LLM behaviors |
| `session-rules.md` | Your timezone, session saving rules, and tracking preferences |

Both are gitignored — personal, never committed. Templates define the recommended practice; you customize for your workflow.

---

## When user says use an agent

| Step | Action |
|---|---|
| 1 | Go to `agents/` |
| 2 | Find best agent for the task |
| 3 | Read that agent file |
| 4 | Do task using that agent's job and limits |

If many agents fit, pick best match.
If no agent fits, say no good agent found, then continue with memory and rules only.

---

## When task needs a skill

| Step | Action |
|---|---|
| 1 | Go to `skills/` |
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
| Coding (implement, fix, refactor) | `rules/coding-rules.md` |
| Creating or editing `.md` files | auto-run `md-to-html` after save (per `memory.md`) |

If multiple apply, read all matching files before starting.

---

## Priority order

| Priority | Source |
|---|---|
| 1 | User instruction |
| 2 | `memory.md` at `.local` folder |
| 3 | Chosen agent from `agents/` |
| 4 | Chosen skill from `skills/` |
| 5 | On-demand rules from `rules/` |
| 6 | `AGENTS.md` rules |
| 7 | Default AI behavior |

---

## Missing files

| Rule | Detail |
|---|---|
| Missing file | Say it clearly. Do not pretend it exists. |
| Optional files | Skip gracefully if not present. |
| Required files | Stop and notify user if `AGENTS.md` is missing. |

---

## .ai folder structure — LLM navigation guide

Use this map to find skills, plugins, agents, and prompts fast.

| Folder | Purpose | How to use |
|---|---|---|
| `.ai/agents/` | Agent definitions — each file is one agent with job + limits | Read the file, do the task using its rules |
| `.ai/skills/` | Reusable skills — each subfolder is one skill | Read the skill file, follow its workflow |
| `.ai/plugins/` | Plugins — each subfolder is one plugin | Read the plugin file, use its tools |
| `.ai/prompts/` | Prompt templates — reusable LLM prompts | Read the prompt, fill in variables, execute |
| `.ai/rules/` | Coding + PR rules | Reference when implementing or fixing PRs |
| `.ai/copilot/` | GitHub Copilot specific instructions | Loaded by Copilot only |

### Finding the right file

1. **Need a task-specific agent?** → `.ai/agents/` → pick by name
2. **Need a reusable workflow?** → `.ai/skills/` → pick by name
3. **Need a plugin tool?** → `.ai/plugins/` → pick by name
4. **Need a prompt template?** → `.ai/prompts/` → check `index.md` first for description
5. **Need coding or PR rules?** → `.ai/rules/` → read the matching `.md`

### Index files

When a folder has `index.md`, read it first — it maps names to purposes.
When a folder has `README.md`, read it for usage instructions.

No index? List the folder and read filenames to decide.

---

## Sync scripts

### macOS / Ubuntu — `sync.sh`

```bash
#!/bin/bash
mkdir -p .ai
cp AGENTS.md CLAUDE.md
cp AGENTS.md GEMINI.md
cp AGENTS.md .windsurfrules
cp AGENTS.md .codeiumrules
cp AGENTS.md CONVENTIONS.md
cp AGENTS.md .rules
cp AGENTS.md .github/copilot-instructions.md
echo "AI rules synced."
```

Make it executable and run:

```bash
chmod +x sync.sh
./sync.sh
```

### Windows — `sync.ps1`

```powershell
New-Item -ItemType Directory -Force -Path .ai | Out-Null
Copy-Item AGENTS.md CLAUDE.md
Copy-Item AGENTS.md GEMINI.md
Copy-Item AGENTS.md .windsurfrules
Copy-Item AGENTS.md .codeiumrules
Copy-Item AGENTS.md CONVENTIONS.md
Copy-Item AGENTS.md .rules
Copy-Item AGENTS.md .github\copilot-instructions.md
Write-Host "AI rules synced."
```

Run:

```powershell
.\sync.ps1
```

---

## When to sync

| Trigger | Action |
|---|---|
| After editing `AGENTS.md` | Run sync script |
| Before committing | Run sync script |
| After pulling changes to `AGENTS.md` | Run sync script |

---

## Project sync — copy .ai folder to another project

One-way sync of the entire `.ai` folder to another project. Edit the target path in `sync.bat` and run:

```cmd
sync.bat
```

Uses `robocopy /MIR` (mirror mode) — adds new files, updates changed files, removes deleted files. Excludes `.git`, `__pycache__`, `.local`.

Edit the `TARGET` variable in `sync.bat` to point to your project before running.

---

## Optional: auto-sync on commit (Git hook)

```bash
# .git/hooks/pre-commit
#!/bin/bash
./sync.sh
git add CLAUDE.md GEMINI.md .windsurfrules .codeiumrules CONVENTIONS.md .rules .github/copilot-instructions.md
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```
