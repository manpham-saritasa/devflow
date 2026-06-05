# AI Agent Behaviors

> Use these rules when communicating with user or creating/editing files for user.

## 1. Communication
- When executing a skill, prefix every message with `[skill-name]` (e.g. `[dev-start] ✅ Branch ready:`).
- End completed actions with `✅ Done.` — after statements, never after questions.
- Prefix every question to me with `❓` — do not add `✅ Done.` on the same line.
- Number every question so I can answer by number (e.g. `❓1. A? 2. B?`)
- If there are many solutions to choose, always show your chosen solution on top and add to the last a new option that say "Show me the detailed changes first, for option #1".
- If unsure, say so.
- For answers, include confidence as `/10`:
  - 🟢 high
  - 🟠 medium
  - 🔴 low
- For multi-item answers, sort by highest confidence first.
- Prefer tables over bullet lists whenever possible. Tables are easier to scan.
- Always format URLs as clickable markdown links: `[text](url)`. Never output plain URLs.
- When I start a sentence with `:`, do not act yet. Clarify: restate my intention, the action, target, and any context — so I can confirm you understood before proceeding.
- Use caveman mode when talking to me directly:
  - short
  - simple
  - direct
  - minimal fluff
  - easy scan
- When drafting open questions or answers about the project, try reading `.local/project-info/` first (if it exists) to avoid asking things already documented there.
- Use student mode when drafting messages for my team or clients:
  - clear
  - polite
  - structured
  - natural professional tone
  - complete sentences

---

## 2. Shortcuts (customize for your workflow)

| Shortcut | Action |
|---|---|
| `cush` | Commit using `dev-commit` skill, then push all to origin |
| `reload` | Re-read: memory.md, startup.md, AGENTS.md, rules/coding-rules.md, rules/session-rules.md |
| `devflow` | Run the devflow agent from `.ai/agents/devflow.md` |
| `creport` | Run the `change-report` skill — auto-detects preview vs after mode |
| `html` | Re-run `md-to-html` for all recently created/edited `.md` files in this chat |
| `md-view` | Start the `md-view` server for browser-based .md preview |
| `docx` | Re-run `md-to-docx` skill for recently created/edited `.md` files in this session |
| `pr-only` | Ship PR without Jira (`dev-ship --pr-only`) |
| `wt KEY` | Start with worktree (`dev-start --worktree KEY`) |
| `done` | Finish task: merge PR + delete worktree + cleanup (`dev-finish`). Also save session. |
| `ship` | `cush` first, then run `dev-ship` for the branch's task key. Also save session. |
| `save` | Save session snapshot to `.local/sessions/raw/YYYY-MM-DD.md` |
| `learnt` | After any task — reflect: what rules/principles emerged? What patterns can generalize? Propose additions to `coding-rules.md`. |

## 3. Creating markdown files or text documents
- Big `##` section come, put `---` first.
- Every big `##` need number in markdown file.
- Do not include any secret values, my personal info, company info, or real project info into any files.
- Do not include the absolute local path of my computer into any files.

- When creating AI's prompts, skills, plugins, or agents:
  - keep them generic, configurable, reusable, and easy to share
  - move reusable vars, paths, URLs, and common constants to the top
  - move detection conditions/logic to the top
  - keep wording minimal and caveman-style

- When creating markdown documents:
  - use student mode, not caveman mode so that the text is not too long or too short and still understandable
  - run the `review-md` skill to review the md file content
