# devflow-sync

Sync AI workflow files from the devflow toolkit into your projects.

## Install

```bash
npm install -g devflow-sync
```

## Quick start

```bash
# In your project:
npx devflow-sync init
```

Interactive setup — choose which components and AI tools to sync.

## Commands

| Command | Description |
|---------|-------------|
| `init` | Interactive first-time setup. Creates `.devflow.json`. |
| `update` | Re-sync using existing `.devflow.json`. |
| `update --dry-run` | Preview files without writing. |

## What gets synced

| Component | Destination | Content |
|-----------|-------------|---------|
| Agents | `.ai/agents/` | Planner, coder, reviewer workflows |
| Skills | `.ai/skills/` | Automation skills (review, refactor, convert) |
| Plugins | `.ai/plugins/` | Full plugin suites (devflow, refflow, jiraflow) |
| Prompts | `.ai/prompts/` | Reusable prompt templates |
| Instructions | `.ai/instructions/` | Coding and communication rules |
| Startup | `.ai/startup.md` | Session entry point |
| Rules | `.ai/rules/` | PR rules, coding rules, session rules |

## AI tool support

| Tool | Files synced |
|------|-------------|
| Claude | `CLAUDE.md`, `.claude/skills/` wrappers, `.claude/agents/` |
| Copilot | `.github/copilot-instructions.md`, `.ai/copilot/` |
| Cursor | `.cursor/rules/main.mdc` (pointer to `AGENTS.md`) |
| Windsurf | `.windsurfrules` |
| Codeium | `.codeiumrules` |
| Zed / JetBrains | `.rules` |
| Gemini | `GEMINI.md` |
| Aider | `CONVENTIONS.md` |

## Config

`.devflow.json`:

```json
{
  "version": "1.0.0",
  "tools": ["claude", "copilot", "cursor"],
  "components": ["agents", "skills", "startup", "rules"],
  "skills": ["review-md", "quick-refactor"],
  "conflictMode": "backup"
}
```

| Field | Description |
|-------|-------------|
| `tools` | AI tools to generate config files for |
| `components` | Component types to sync |
| `skills` | Specific skills (null = all) |
| `conflictMode` | `overwrite` / `backup` / `skip` |

## Conflict handling

| Mode | Behavior |
|------|----------|
| `overwrite` | Replace existing files |
| `backup` | Rename existing to `.devflow.bak`, then write |
| `skip` | Keep existing files untouched |

## Development (local)

Requirements: Node.js 18+, Git.

```bash
cd cli
npm install
npm run build
npm link
```

Then use `devflow-sync init` from any project.

## Troubleshooting

1. Check Node.js version: `node --version` (needs 18+)
2. Rebuild: `npm run build` (from `cli/`)
3. Re-link: `npm link` (from `cli/`)
4. Re-init: `devflow-sync init` to reconfigure from scratch

## How it works

Files are bundled with the npm package at publish time. `update` copies them from the package into your project. Re-publish the package to distribute new versions.
