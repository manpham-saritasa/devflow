# AI Agent Behaviors

> Use these rules when communicating with user or creating/editing files for user.

## 1. Communication
- Skill execution: prefix every message with `[skill-name]` (e.g. `[dev-start] ✅ Branch ready:`).
- Done actions: end with `✅ Done.` — after statements, never after questions.
- Questions: prefix with `❓`. Never add `✅ Done.` on same line.
- Number every question: `❓1. A? 2. B?`
- Multiple solutions: show chosen solution first. Add "Show detailed changes first, for option #1" as last option.
- If unsure, say so.
- Answers: tag confidence `/10` (🟢 high, 🟠 medium, 🔴 low).
- Multi-item: sort by highest confidence first.
- Prefer tables over bullets. Easier to scan.
- When a plan is needed, show a confirmation table before acting:

  ```
  🚛 Summary: [1-line what these changes achieve]

  | # | File | Change | Category | Why |
  |---|------|--------|----------|-----|
  | 1 | path/file.md | what changes | new/fix/refactor/style/docs/config | reason for change |
  ```
- Always format URLs as clickable markdown links: `[text](url)`. Never output plain URLs.
- Sentence starting with `:` → clarify first. Restate intention, action, target, context. Wait for confirmation.
- Talk to me: caveman mode (short, simple, direct, minimal fluff, easy scan).
- Project questions/answers: read `.local/project-info/` first (if exists). Avoid asking documented info.
- Team/client messages: student mode (clear, polite, structured, natural professional tone, complete sentences).

---

## 2. Shortcuts (customize for your workflow)

| Shortcut | Action |
|---|---|
| `cush` | Commit using `dev-commit` skill, then push all to origin |
| `reload` | Re-read: memory.md, startup.md, AGENTS.md, rules/coding.md, .local/session-rules.md |
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
| `review` | Review changes LLM just made: 1–2 .md files → use `review-md`; multiple .md / skill-design files → use `review-design`; code files → use `review-code`. |

## 3. Terminal commands
- Check `rtk` availability on session start. If available, ALWAYS prefix supported CLI commands: `rtk git ...`, `rtk gh ...`, `rtk pytest`, etc. Never run raw commands that RTK supports. Run `rtk --help` for full list.

## 4. Code quality thresholds

After editing `.py`, `.cs`, or `.php` files — run threshold check before continuing:

```bash
python .ai/skills/check-thresholds/scripts/scan.py --changed <edited files>
```

- Exit 0 (✅ All thresholds met.) → continue.
- Exit 1 (violations) → fix violations before next step. Report: `❌ N violations — fixing.`
- Never skip. Never hand-wave. Run the command.

Thresholds: file ≤300 lines, function ≤40 lines, params ≤4.

---

## 5. Creating markdown files or text documents
- Big `##` section come, put `---` first.
- Every big `##` needs number.
- No secrets, personal info, company info, real project info in files.
- No absolute local paths.
- AI prompts/skills/plugins/agents: generic, configurable, reusable. Move vars/paths/URLs/constants to top. Move conditions to top. Caveman-style wording.
- Markdown docs: student mode (not too long, not too short, understandable). Run `review-md` after.
- `.md` with matching `.html` → regenerate HTML via `md-to-html`.
- `jlog`: format as clean table in chat. Never dump raw terminal output.

---

## 6. Skill script design

Skill scripts are data pipelines, not content generators.

| Layer | Responsibility | Who |
|---|---|---|
| Extract | Fetch raw data from APIs (Gmail, Jira, GitHub) | Script |
| Resolve | Look up IDs against metadata (component IDs, field IDs, sprint IDs) | Script |
| Decide | What to say, how to summarize, which type/component fits the context | **LLM** |
| Execute | Call external APIs with LLM-provided values | Script |

Rules:
- Never guess issue type, component, or priority from keywords in script code.
- Never build summaries, descriptions, reply text, or acceptance criteria in script code.
- All content values flow through CLI args (`--summary`, `--description`, `--environment`, `--reply-body`).
- Script fallbacks for content are anti-pattern. Empty string > wrong guess.
- After removing a content-generating function, audit for orphaned imports and dead modules (`grep` for the function name across the plugin).
