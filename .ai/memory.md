# AI Agent Behaviors

> Use these rules when communicating with user or creating/editing files for user.

## 1. Communication
- Before each big section, put `---` first.
- Always end completed work messages with `✅ Done.`
- Prefix every question to me with `❓`
- Number every question so I can answer by number (e.g. `❓1. A? 2. B?`)
- For answers, use confidence format from `AGENTS.md`.
- For multi-item answers, sort by highest confidence first.
- Use caveman mode when talking to me directly:
  - short
  - simple
  - direct
  - minimal fluff
  - easy scan
- Use student mode when drafting messages for my team or clients:
  - clear
  - polite
  - structured
  - natural professional tone
  - complete sentences

---

## 2. Shortcuts

| Shortcut | Action |
|---|---|
| `cush` | Commit and push all to origin |
| `reload` | Re-read: memory.md, startup.md, AGENTS.md, rules/coding-rules.md, rules/pr-rules.md |
| `devflow` | Run the devflow agent from `.ai/plugins/devflow/` |
| `html` | Re-run `md-to-html` skill for recently created/edited `.md` files in this session |
| `docx` | Re-run `md-to-docx` skill for recently created/edited `.md` files in this session |
| `pr-only` | Ship PR without Jira (`dev-ship --pr-only`) |
| `wt KEY` | Start with worktree (`dev-start --worktree KEY`) |
| `done` | Finish task: merge PR + delete worktree + cleanup (`dev-finish`) |

## 2. Creating markdown files or text documents
- Big `##` section come, put `---` first.
- Every big `##` need number in markdown file.
- Do not include any secret values, my personal info, company info, or real project info into any files.
- Do not include the absolute local path of my computer into any files.

- When creating AI's prompts, skills, plugins, or agents:
  - keep them generic, configurable, reusable, and easy to share
  - move reusable vars, paths, URLs, and common constants to the top
  - move detection conditions/logic to the top
  - keep wording minimal and caveman-style

- When creating documents:
  - use student mode, not caveman mode so that the text is not too long or too short and still understandable
- When creating or editing `.md` files, always run the `md-to-html` skill to generate the corresponding `.html` file.
