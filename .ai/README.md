# .ai — AI Coding Framework

Suggested rules, skills, and agents for consistent AI-assisted development. LLM-agnostic — works with Zed, Cursor, Copilot, Claude Code, Gemini CLI, Windsurf, Codeium, Aider, JetBrains AI.

---

## Two-Layer Architecture

| Layer | Location | Shared? |
|-------|----------|---------|
| **Framework** | `.ai/` (rules, skills, agents, plugins) | ✅ Git tracked — suggested defaults |
| **Personal** | `.local/` (memory, session-rules, corrections) | ❌ Gitignored — dev-specific |

---

## Quick Deploy

```bash
# Copy framework into target repo
cp -r .ai/ target-repo/
```

Done. Each dev pastes the 1-line router into their AI tool's config file (see table below).

---

## Set Up Your Personal Workspace

Each teammate customizes `.local/` (gitignored, never committed):

```bash
# Windows (PowerShell)
Copy-Item .ai/rules/memory.md.template .local/memory.md
Copy-Item .ai/rules/session-rules.md.template .local/session-rules.md

# Unix / macOS
cp .ai/rules/memory.md.template .local/memory.md
cp .ai/rules/session-rules.md.template .local/session-rules.md
```

| File | Purpose |
|------|---------|
| `memory.md` | Shortcuts (`cush`, `ship`, `creport`), comm style, LLM behaviors |
| `session-rules.md` | Timezone, session saving, tracking |

---

## Supported LLMs — 1-Line Setup

Paste this line into your tool's config file:

```
Read `.ai/startup.md` first — it loads all rules, memory, and corrections for this session.
```

| LLM | File to update | Project location |
|-----|---------------|-----------------|
| Zed | `AGENTS.md` | `<repo>/AGENTS.md` |
| Cursor | `.cursorrules` / `.cursor/rules/main.mdc` | `<repo>/.cursor/rules/main.mdc` |
| Copilot | `copilot-instructions.md` | `<repo>/.github/copilot-instructions.md` |
| Claude Code | `CLAUDE.md` | `<repo>/CLAUDE.md` |
| Gemini CLI | `GEMINI.md` | `<repo>/GEMINI.md` |
| Windsurf | `.windsurfrules` | `<repo>/.windsurfrules` |
| Codeium | `CODEIUM.md` | `<repo>/CODEIUM.md` |
| Aider | `CONVENTIONS.md` | `<repo>/CONVENTIONS.md` |
| JetBrains | `.aia/instructions.md` | `<repo>/.ijwb/.aia/instructions.md` |

Project location = checked into git, shared with team.

---

## Folder Map

| Folder | Purpose | When loaded |
|--------|---------|-------------|
| `.ai/rules/` | Framework rules, coding rules, templates | `core.md` via startup.md, `coding.md` on-demand |
| `.ai/agents/` | Agent definitions — job + limits per agent | On `devflow` / `refflow` invocation |
| `.ai/skills/` | Reusable skills — each subfolder = 1 skill | On skill invocation |
| `.ai/plugins/` | Plugin bundles (DevFlow, RefFlow, JiraFlow, GithubFlow) | On skill invocation |
| `.ai/prompts/` | Prompt templates | On demand |
| `.ai/copilot/` | Copilot-specific instructions | By Copilot |

Root files (AGENTS.md, etc.) are thin routers pointing into `.ai/`. Each dev sets up their own via their AI tool's config.

---

## Rules Loading (Token-Efficient)

| Tier | Files | When | ~Size |
|------|-------|------|-------|
| **Tier 0 — Always** | AGENTS.md (1-line router, per-dev) | Auto-loaded by AI tool | 1 line |
| **Tier 1 — Startup** | `startup.md` → `core.md` | Session start | ~5 KB |
| **Tier 2 — Personal** | `.local/memory.md`, `session-rules.md` | Startup (optional) | User-defined |
| **Tier 3 — On-demand** | `coding.md` | First code task | ~3 KB |
| **Tier 4 — Lazy** | Skills, agents, plugins | On invocation | Pay-per-use |
| **Tier 5 — Reference** | `corrections.md` | Startup (mistakes to avoid) | ~1 KB |

Nothing duplicated across tiers. Nothing loaded until needed.

---

## Adding a New AI Tool

1. Add a row to the Supported LLMs table above
2. Done — no other files change
