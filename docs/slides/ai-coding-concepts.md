# AI Coding Concepts for Local Dev

## Slide 1 — Title
- AI Coding Concepts for Local Dev.
- Prompts, rules, skills, agents, tools, context, and memory.

## Slide 2 — Why this matters
- Same repo, different AI setups, different results.
- Shared setup makes output more consistent.
- Goal: less guesswork, better team workflow.

## Slide 3 — Big picture
- Prompt tells the AI what to do.
- Context gives the AI what it can see now.
- Memory keeps what should survive later.
- Rules constrain behavior.
- Skills package repeatable workflows.
- Tools let the AI act.
- Agent combines them into execution.

## Slide 4 — LLM concept
- LLM = language model that predicts the next tokens.
- Good at drafting, explaining, transforming, and summarizing.
- Not a source of truth.
- Must be checked with real files, tests, and outputs.

## Slide 5 — Tokens and context
- Token = chunk of text, not exactly a word.
- Context window = how much the model can use now.
- Prompt, files, tool output, chat history all consume context.
- Bigger context helps, but too much noise hurts.

## Slide 6 — Session concept
- Session = the current working conversation.
- It includes prompts, replies, tool calls, and temporary state.
- Session is larger than the context sent on one turn.
- Session is often temporary.

## Slide 7 — Diagram
```text
Prompt + files + rules + memory + tool output
                    |
                    v
                 Tokens
                    |
                    v
            Current context window
                    |
                    v
                   LLM
                    |
                    v
        Response + tool actions + new state
                    |
                    v
              Working session
```
- Session is the workspace.
- Context is the slice sent now.

## Slide 8 — Session limits
- Session may be lost next time.
- Long sessions get noisy.
- Important decisions can disappear in chat.
- Write key state to repo files.

## Slide 9 — Memory concept
- Memory = stored information reused later.
- Short-term memory = current session and context.
- Long-term memory = external storage around the model.
- Common team pattern: Markdown memory files.

## Slide 10 — File-based memory
- Pros: simple, visible, versioned, cross-tool.
- Pros: easy for humans and LLMs to read.
- Cons: can get stale, noisy, duplicated.
- Cons: large files reduce relevance.
- Keep memory small and curated.

## Slide 11 — Context rot
- Quality drops when context gets too long or noisy.
- Model may forget earlier constraints.
- More context is not always better.
- Use fresh sessions and task-focused context.

## Slide 12 — Hallucinations
- AI can invent files, APIs, facts, or behavior.
- Confident tone does not mean correct output.
- Hallucinations increase with vague or noisy context.
- Verify with code, tests, grep, and build output.

## Slide 13 — Other failure modes
- Omission: skips an important step or requirement.
- Instruction drift: starts right, then ignores earlier constraints.
- Overconfidence: sounds certain when it should be uncertain.
- Tool misuse: picks the wrong tool or wrong parameters.
- Goal drift: starts solving a different problem.
- False completion: says done before the real task is complete.

## Slide 14 — Prompt concept
- Prompt = instruction package for this task.
- Can include goal, context, constraints, format, examples.
- Good prompts reduce ambiguity.
- Structure matters more than length.

## Slide 15 — Prompt usage example
- Bug fix: describe symptom, file, expected behavior, ask for minimal change + test.
- Refactor: state goal, files in scope, keep behavior, list tests to keep passing.


## Slide 16 — Big prompt example
```text
Create a cinematic hero image for an internal engineering presentation.
Subject: senior engineer, 3 monitors, code, Git graph, AI panel.
Style: modern editorial, detailed, professional.
Scene: night office, blue-teal glow, practical desk setup.
Composition: 16:9, subject left, empty space right for title.
Constraints: no logo, no broken hands, no extra fingers.
Intent: trustworthy, practical, team presentation cover.
```
- Big prompt is fine when every section adds signal.

## Slide 17 — Prompt - PROS
- Fastest way to steer output.
- Easy to change per task.
- Can encode structure and format.
- Works across tools.

## Slide 18 — Prompt - CONS
- Vague prompt, vague result.
- Too many scripts and templates reduce focus.
- Hard to debug when huge.
- Easy to forget constraints over time.

## Slide 19 — Skill concept
- Skill = reusable workflow for a repeated job.
- Can include instructions, examples, scripts, references.
- Good for review, refactor, bug fix, docs, test generation.
- Load only when relevant.

## Slide 20 — Skill usage example
- Have a /review-skill for PR review, used on every PR.
- Have a /refactor-skill for legacy cleanup tasks.


## Slide 21 — Skill - PROS
- Reusable.
- Faster.
- More consistent.
- Captures team know-how.

## Slide 22 — Skill - CONS
- Overlap causes confusion.
- Old skills become outdated.
- Too many skills are hard to discover.
- Needs pruning.

## Slide 23 — Agent concept
- Agent = AI worker that can think and act in steps.
- Uses prompts, context, memory, rules, skills, and tools.
- Better for multi-step work than plain chat.
- More autonomy means more risk.

## Slide 24 — Agent usage example
- Use coding agent for "implement feature X" with branch + tests.
- Use research agent to gather APIs and summarize options before coding.


## Slide 25 — Agent - PROS
- Can plan and break down work.
- Can inspect files and run tools.
- Can iterate toward a goal.
- Good for bigger coding tasks.

## Slide 26 — Agent - CONS
- Can drift or overreach.
- May misuse tools.
- Harder to predict.
- Needs boundaries and review.

## Slide 27 — Rule concept
- Rule = instruction that should apply across many tasks.
- Covers safety, coding style, architecture, review limits.
- Rules reduce repeated prompting.
- Rules define what AI must always do or avoid.

## Slide 28 — Rule usage example
- CLAUDE.md: always run tests before saying task is done.
- AGENTS.md: never change public APIs without explicit request.


## Slide 29 — Rule - PROS
- Consistency.
- Safety.
- Team alignment.
- Reusable across sessions and tools.

## Slide 30 — Rule - CONS
- Too many rules become noise.
- Duplicated rules can conflict.
- Hard to maintain if spread around.
- Needs clear owners.




## Slide 31 — Plugin / tool concept
- Tool or plugin lets the AI act outside plain text.
- Examples: file read, search, terminal, Git, API.
- Tools reduce guessing by bringing real evidence.
- Model thinks; tools act.

## Slide 32 — Tool usage example
- File tool: load only files in scope before asking for changes.
- Test tool: run tests and report failures before claiming done.


## Slide 33 — Tool - PROS
- Better evidence.
- Less guessing.
- Enables real workflows.
- Connects AI to real systems.

## Slide 34 — Tool - CONS
- Wrong permissions create risk.
- Too many tools add confusion.
- Bad tool choice wastes time.
- Needs safe defaults and clear scope.

## Slide 35 — Local repo setup
- `AGENTS.md` for shared agent guidance.
- `CLAUDE.md` for Claude-specific onboarding.
- `.ai/memory.md` for persistent project memory.
- `.ai/agents/` for task agents or skills.
- Keep root files short.

## Slide 36 — Team workflow
- Start with clear task prompt.
- Load only needed context.
- Use shared rules and memory.
- Run tools for evidence.
- Review diffs and tests before merge.

## Slide 37 — Team policy
- One source of truth for rules.
- Small prompts, small memory, small skills.
- Store durable knowledge in files, not chat only.
- Every AI change is review-required.