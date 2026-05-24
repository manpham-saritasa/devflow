# AI Coding Setup on Local Dev

## Slide 1 — Title
- **Title:** AI Coding Setup on Local Dev
- **Subtitle:** Prompts, skills, plugins, rules, and shared repo instructions
- **Speaker note:** Focus on team workflow, not vendor marketing.

## Slide 2 — Why standardize this
- Different AI coding tools can work well, but results become inconsistent when each developer uses different prompts, rules, and folder conventions.
- A shared local setup makes outputs more predictable, easier to review, and easier to scale across a team.
- Goal: one repo memory model, many tools.

## Slide 3 — Core concepts
- **LLM:** The model that reads instructions and generates output.
- **Prompt:** The task request for the current session.
- **Rules:** Persistent repo instructions the model should follow every time.
- **Skill:** Reusable task guidance or helper package for specific jobs.
- **Plugin / tool:** External capability such as file access, terminal, Git, test runner, or browser actions.

## Slide 4 — The local setup layers
- **Layer 1:** User prompt, the task we ask right now.
- **Layer 2:** Repo instructions, such as `CLAUDE.md`, `AGENTS.md`, or Copilot custom instructions.
- **Layer 3:** Nested or subproject instructions for specific folders or services.
- **Layer 4:** Project memory, rules, and task agents in agreed paths like `.ai/memory.md`, `.rules`, and `.ai/agents/`.

## Slide 5 — Recommended repo structure
- Suggested root files: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and optional tool-specific files if needed.
- Suggested shared support folders: `.ai/memory.md`, `.ai/agents/`, and one rules location such as `.rules` or `.ai/rules.md`.
- Team principle: keep one canonical source of truth, then sync or reference it into tool-specific files.

## Slide 6 — What goes in AGENTS.md
- Use `AGENTS.md` as the repo-level README for coding agents.
- Include project overview, stack map, build and test commands, code style rules, testing expectations, security notes, and PR guidance.
- In larger repos, add nested `AGENTS.md` files for subprojects when needed.

## Slide 7 — What goes in CLAUDE.md
- Use `CLAUDE.md` to onboard Claude into the codebase using the project’s what, why, and how.
- Keep it concise, stable, and easy to scan.
- Point to deeper files for rules, architecture, or task-specific details instead of copying everything into one long document.

## Slide 8 — Copilot and other tools
- GitHub Copilot supports repository custom instructions so it can understand the project and know how to build, test, and validate changes.
- Different tools still use different filenames and conventions.
- That is why a shared internal convention plus sync strategy is useful for local development.

## Slide 9 — Canonical file strategy
- Use one canonical file as the main human-edited source, usually `AGENTS.md` or another shared rules document.
- Mirror or reference that content into `CLAUDE.md`, `.github/copilot-instructions.md`, and any other required tool file.
- Keep common rules centralized so changes are made once and propagated everywhere.

## Slide 10 — Prompt setup standard
- Prompts should be short, direct, and structured with clear sections instead of loose paragraphs.
- Strong internal pattern: `Goals`, `Current context`, `Plan / actions`, `Risks`, and `Next steps`.
- For coding work, also include success criteria, files in scope, and when the model must stop and ask.

## Slide 11 — Rules setup standard
- Rules should be durable, model-readable, and not tied to temporary implementation details.
- Good rule topics: safety, scope control, reuse over copy-paste, code style alignment, testing, and review triggers.
- Rules should tell the model what to do when uncertain, such as ask when scope, behavior, or risk is unclear.

## Slide 12 — Skills and task agents
- Skills are better for repeatable workflows such as bug fixing, refactoring, design review, PR summary writing, or test generation.
- Keep task-specific agents under `.ai/agents/` and shared project memory in `.ai/memory.md`.
- This separates stable project rules from specialized task behavior.

## Slide 13 — Local workflow example
- Step 1: Open the repo in a tool that reads its instruction files.
- Step 2: The tool loads repo guidance from `CLAUDE.md`, `AGENTS.md`, Copilot instructions, or equivalent files.
- Step 3: Give a task prompt with clear scope and output requirements.
- Step 4: The model reads extra rules, memory, or task agents only when relevant.
- Step 5: Review diffs, run tests, and approve changes before merge.

## Slide 14 — Suggested file template
- `AGENTS.md`: repo overview, stack map, commands, coding rules, validation steps, review rules.
- `CLAUDE.md`: short onboarding file, what / why / how, plus pointers to deeper docs.
- `.ai/memory.md`: long-lived project context, domain notes, architecture facts, important decisions.
- `.ai/agents/`: task-focused agent prompts or skills such as review, refactor, docs, tests.
- `.rules` or `.ai/rules.md`: compact universal coding rules that any model can read.

## Slide 15 — Team policy proposal
- Keep one canonical AI instruction source and sync it to tool-specific files when needed.
- Keep root files short; move deep detail into referenced documents.
- Prefer structured prompts, shared rule files, and task agents over ad hoc one-off prompting.
- Treat every AI-generated change as review-required, even when the local setup is strong.
