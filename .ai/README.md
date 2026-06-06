# .ai — AI Coding Setup

Drop-in package that gives any project consistent AI assistant behavior. LLM-agnostic — works with Zed, Cursor, Copilot, Claude Code, Gemini CLI, Windsurf, Codeium, Aider, JetBrains AI.

---

## Quick Deploy

```bash
# 1. Copy the package into target repo
cp -r .ai/ target-repo/

# 2. Run sync for your AI tool
cd target-repo
./.ai/sync/sync.ps1 zed     # or: cursor, copilot, claude, gemini, windsurf, codeium, aider, jetbrains
```

Done — your AI tool auto-detects its rules file.

---

## Folder Map

| Folder | Purpose | When loaded |
|--------|---------|-------------|
| `.ai/rules/` | Core rules + coding rules + templates | `core.md` always, `coding-rules.md` on-demand |
| `.ai/agents/` | Agent definitions — job + limits per agent | On `devflow` / `refflow` invocation |
| `.ai/skills/` | Reusable skills — each subfolder = 1 skill | On skill invocation |
| `.ai/plugins/` | Plugin bundles (DevFlow, RefFlow, JiraFlow, GithubFlow) | On skill invocation |
| `.ai/prompts/` | Prompt templates | On demand |
| `.ai/copilot/` | Copilot-specific instructions | By Copilot |

Root files are **all generated** — run `.ai/sync/sync.ps1` / `.ai/sync/sync.sh` to create them. Never edit root files directly.

---

## Rules Loading (Token-Efficient)

| Tier | Files | When | ~Size |
|------|-------|------|-------|
| **Tier 0 — Always** | `.ai/rules/core.md` | Auto-loaded by AI tool | 4 KB |
| **Tier 1 — Startup** | `startup.md` | Session start | 2 KB |
| **Tier 2 — Personal** | `.local/memory.md`, `session-rules.md` | Startup (optional) | User-defined |
| **Tier 3 — On-demand** | `coding-rules.md` | First code task | 3 KB |
| **Tier 4 — Lazy** | Skills, agents, plugins | On invocation | Pay-per-use |
| **Tier 5 — Reference** | `corrections.md` | Startup (mistakes to avoid) | ~1 KB |

Nothing duplicated across tiers. Nothing loaded until needed.

---

## Set Up Your Personal Workspace

Each teammate customizes `.local/` (gitignored, never committed):

```bash
cp .ai/rules/memory.md.template .local/memory.md
cp .ai/rules/session-rules.md.template .local/session-rules.md
```

| File | Purpose |
|------|---------|
| `memory.md` | Shortcuts (`cush`, `ship`, `creport`), comm style, LLM behaviors |
| `session-rules.md` | Timezone, session saving, tracking |

---

## Sync Scripts

### `sync.ps1` (Windows)

```powershell
. .ai/sync/sync.ps1 zed       # creates .rules symlink
. .ai/sync/sync.ps1 cursor    # creates .cursor/rules/main.mdc copy
. .ai/sync/sync.ps1 all       # creates all tool files
```

### `sync.sh` (macOS/Linux)

```bash
./.ai/sync/sync.sh zed        # creates .rules symlink
./.ai/sync/sync.sh cursor     # creates .cursor/rules/main.mdc copy
./.ai/sync/sync.sh all        # creates all tool files
```

---

## Adding a New AI Tool

1. Add target path to `.ai/sync/sync.ps1` and `.ai/sync/sync.sh`
2. Done — no other files change
