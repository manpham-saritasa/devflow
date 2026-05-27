# AI Coding Concepts for Local Dev

Prompts, rules, skills, agents, tools, context, and memory.

---

## Why this matters

- Same repo, different AI setups, different results.
- Shared setup makes output more consistent.
- Goal: less guesswork, better team workflow.

---

## Big picture

- Prompt tells the AI what to do.
- Context gives the AI what it can see now.
- Memory keeps what should survive later.
- Rules constrain behavior.
- Skills package repeatable workflows.
- Plugins automate real actions.
- Agent combines them into execution.

---

## LLM concept

- LLM = language model that predicts the next tokens.
- Good at drafting, explaining, transforming, and summarizing.
- Not a source of truth.
- Must be checked with real files, tests, and outputs.

---

## Tokens and context

- Token = chunk of text, not exactly a word.
- Context window = how much the model can use now.
- Prompt, files, tool output, chat history all consume context.
- Bigger context helps, but too much noise hurts.

---

## Session concept

- Session = the current working conversation.
- It includes prompts, replies, tool calls, and temporary state.
- Session is larger than the context sent on one turn.
- Session is often temporary.

---

## How it flows

Prompt + files + rules + memory + tool output → Tokens → Context window → LLM → Response + actions → Working session

- Session is the workspace.
- Context is the slice sent now.

---

## Session limits

- Session may be lost next time.
- Long sessions get noisy.
- Important decisions can disappear in chat.
- Write key state to repo files.

---

## Memory concept

- Memory = stored information reused later.
- Short-term memory = current session and context.
- Long-term memory = external storage around the model.
- Common team pattern: Markdown memory files.

---

## File-based memory

- Pros: simple, visible, versioned, cross-tool.
- Cons: can get stale, noisy, duplicated, large files reduce relevance.
- Keep memory small and curated.

---

## Context rot

- Quality drops when context gets too long or noisy.
- Model may forget earlier constraints.
- More context is not always better.
- Use fresh sessions and task-focused context.

---

## Hallucinations

- AI can invent files, APIs, facts, or behavior.
- Confident tone does not mean correct output.
- Hallucinations increase with vague or noisy context.
- Verify with code, tests, grep, and build output.

---

## Other failure modes

- Omission: skips an important step or requirement.
- Instruction drift: starts right, then ignores earlier constraints.
- Overconfidence: sounds certain when it should be uncertain.
- Tool misuse: picks the wrong tool or wrong parameters.
- Goal drift: starts solving a different problem.
- False completion: says done before the real task is complete.

---

## Prompt concept

- Prompt = instruction package for this task.
- Can include goal, context, constraints, format, examples.
- Good prompts reduce ambiguity.
- Structure matters more than length.

---

## Prompt usage example

- Bug fix: describe symptom, file, expected behavior, ask for minimal change + test.
- Refactor: state goal, files in scope, keep behavior, list tests to keep passing.

---

## Prompt - PROS & CONS

| PROS | CONS |
|---|---|
| Fastest way to steer output | Vague prompt, vague result |
| Easy to change per task | Too many scripts reduce focus |
| Can encode structure and format | Hard to debug when huge |
| Works across tools | Easy to forget constraints over time |

---

## Skill concept

- Skill = reusable workflow for a repeated job.
- Can include instructions, examples, scripts, references.
- Good for review, refactor, bug fix, docs, test generation.
- Load only when relevant.

---

## Skill usage example

- Have a /review-skill for PR review, used on every PR.
- Have a /refactor-skill for legacy cleanup tasks.

---

## Skill - PROS & CONS

| PROS | CONS |
|---|---|
| Reusable | Overlap causes confusion |
| Faster | Old skills become outdated |
| More consistent | Too many are hard to discover |
| Captures team know-how | Needs pruning |

---

## Prompt vs Skill comparison

| Aspect | Prompt | Skill |
|---|---|---|
| Scope | One task | Repeated job |
| Lifetime | Temporary, inline | Persistent, reusable |
| Complexity | Short to medium | Can include scripts, examples, refs |
| Sharing | Copy-paste | File in repo, versioned |
| Discovery | Hard to find old prompts | Named file, easy to load |
| Overhead | None | Must be written and maintained |
| Runs on | Local or web — depends on AI host | Local — file in repo |
| Uses local scripts or assets | No | Yes — can reference scripts, templates, images |
| Best for | One-off asks, quick steer | Repeated workflows (review, refactor, docs) |

---

## When to use prompt vs skill

- Use prompt when: task is one-off, instruction is short, no reuse expected.
- Use skill when: task repeats, workflow has multiple steps, team needs consistency, worth maintenance cost.

---

## Plugin concept

- Plugin = packaged tool that the AI can invoke to perform real actions.
- Runs scripts, calls APIs, modifies files, executes commands.
- More powerful than a skill — has side effects beyond text.
- Lives in the repo as a folder with instructions, scripts, and config.

---

## Plugin usage example

- `devflow` plugin: commit code, push branches, create PRs, resolve comments.
- `md-to-html` plugin: convert Markdown to styled HTML with one command.
- `db-migration` plugin: generate, validate, and apply database migrations.
- `deploy-check` plugin: run pre-deploy checks and report readiness.

---

## Plugin - PROS & CONS

| PROS | CONS |
|---|---|
| Automates real dev workflows | Higher risk — can mutate, push, deploy |
| Runs locally with full machine access | More complex to build and maintain |
| Versioned in repo — team runs same tools | Platform-dependent (Python, Node, shell) |
| Composable — plugins call other plugins | Needs careful permission design |

---

## Skill vs Plugin comparison

| Aspect | Skill | Plugin |
|---|---|---|
| What it is | Reusable instruction workflow | Packaged tool with actions |
| Runs | Read and followed by LLM | Can run scripts, call APIs, modify files |
| Scope | Guidance + examples | Execution + side effects |
| Risk | Low — only text | Higher — can run code and mutate state |
| Example | `/review-pr` skill | `devflow` plugin with commit, push, PR |
| Runs on | Local — file in repo | Local — on developer machine |
| Uses local scripts or assets | Can reference them | Can execute them directly |
| Best for | Consistent process, team know-how | Automating real dev actions |

---

## When to use skill vs plugin

- Use skill when: you need a repeatable guide, no code execution needed, safe to share as markdown.
- Use plugin when: you need to run scripts or tools, workflow has side effects (commit, deploy), worth added complexity.

---

## Rule concept

- Rule = instruction that should apply across many tasks.
- Covers safety, coding style, architecture, review limits.
- Rules reduce repeated prompting.
- Rules define what AI must always do or avoid.

---

## Rule usage example

- CLAUDE.md: always run tests before saying task is done.
- AGENTS.md: never change public APIs without explicit request.

---

## Rule - PROS & CONS

| PROS | CONS |
|---|---|
| Consistency | Too many become noise |
| Safety | Duplicated rules can conflict |
| Team alignment | Hard to maintain if spread around |
| Reusable across sessions and tools | Needs clear owners |

---

## Sub-agent concept

- Sub-agent = AI worker spawned by the main agent for a subtask.
- Has its own context window — does not see the main conversation.
- Receives a concrete, self-contained task from the main agent.
- Returns only its final message back.
- Main agent delegates, coordinates, and synthesizes results.

---

## Sub-agent usage example

- Parallel: spawn 3 sub-agents to research APIs, review docs, and scan code at the same time.
- Isolation: give one sub-agent a risky refactor so it cannot touch other files.
- Review: ask a sub-agent to review your diff as a fresh pair of eyes.
- Heavy work: let a sub-agent run tests or builds while you continue planning.

---

## Sub-agent - PROS & CONS

| PROS | CONS |
|---|---|
| Parallel — multiple subtasks at once | Setup cost — good subtasks take care |
| Clean context — only sees what it needs | No shared memory — cannot see prior decisions |
| Scoped writes — no boundary accidents | Duplication — two agents may redo same work |
| Fresh perspective — not biased by history | Coordination overhead — merge results |
| Main agent stays focused | Debugging is harder — errors in sub-agent logs |

---

## AI agent native support comparison

| Concept | Claude Code | GitHub Copilot | Codex CLI | Zed AI | Cursor |
|---|---|---|---|---|---|
| **Prompt** | ✅ Chat input | ✅ Chat input | ✅ Chat input | ✅ Chat input | ✅ Chat input |
| **Rule** | ✅ CLAUDE.md | ✅ `.github/instructions` | ✅ AGENTS.md | ✅ `.rules` / AGENTS.md | ✅ `.cursor/rules` |
| **Skill** | ✅ Custom slash commands | ⚠️ Instructions only | ✅ AGENTS.md sections | ✅ `.rules` file | ✅ `.cursor/rules` |
| **Plugin** | ✅ MCP servers | ❌ No MCP yet | ⚠️ Tool calling | ✅ MCP support | ⚠️ Limited |
| **Sub-agent** | ✅ `spawn_agent` | ⚠️ Agent mode only | ❌ Not available | ✅ `spawn_agent` | ❌ Not available |

---

## Native support notes

- All agents support prompts — that is table stakes.
- Rule support varies by filename: CLAUDE.md, AGENTS.md, .cursor/rules.
- Skills are most fragmented — each agent uses a different file format.
- MCP is the emerging standard for plugins — Claude Code and Zed lead here.
- Sub-agent support is the newest frontier — only Claude Code and Zed have it today.
- Cross-agent portability needs a shared format (like AGENTS.md + MCP).

---

## Orchestration concept

- Orchestration = running multiple AI agents or sub-agents on one machine.
- One main agent spawns and coordinates many sub-agents in parallel or sequence.
- Each sub-agent works on a disjoint slice — no overlapping file writes.
- The orchestrator merges results, resolves conflicts, and decides next steps.
- Think of it like a tech lead delegating to multiple devs at once.

---

## Orchestration usage example

- Feature build: agent A does data model, agent B does API, agent C does UI — all in parallel.
- Bug hunt: spawn 5 sub-agents to search 5 modules for root cause simultaneously.
- Code review: one sub-agent checks security, another checks style, another checks tests.
- Migration: parallel agents handle different tables or services with isolated write scopes.

---

## Orchestration - PROS & CONS

| PROS | CONS |
|---|---|
| Massive speed-up — 10 min → 2 min | Hard to set up — decomposition is a skill |
| Better context — only loads what it needs | Merge conflicts — incompatible outputs |
| Specialization — different skills per agent | Resource heavy — RAM, CPU, API rate limits |
| Natural review boundary — isolated results | Visibility gap — only sees final messages |
| | Debugging chains — one failure blocks downstream |

---

## MCP concept

- MCP = Model Context Protocol.
- Standard way for AI to connect to external tools and data.
- Like a USB-C for AI integrations — one protocol, many devices.
- Client (AI host) ↔ MCP Server ↔ External system.

---

## MCP architecture

AI Host → MCP Client → MCP Protocol (JSON-RPC) → MCP Server → File System / Git Repo / API Service

- Host asks, server acts, result returns.
- Server runs locally or remote.
- One server can expose multiple tools.

---

## MCP usage + Tool definition

- File system server: read, write, search files with permission control.
- Git server: list branches, view diffs, create commits.
- Database server: run read-only queries, inspect schema.
- API server: fetch issues, PRs, docs from external services.
- Each tool is defined as JSON Schema — the AI reads it to decide when and how to call.
- Example: `read_file` tool with `path` (string) and `start_line` (integer) parameters.

---

## MCP - PROS & CONS

| PROS | CONS |
|---|---|
| One standard instead of N integrations | Still early — spec and ecosystem evolving |
| Tools are discoverable and self-describing | Server quality varies |
| Permission model built in | Local servers need setup and maintenance |
| Community servers growing fast | Remote servers add latency and auth complexity |
| Works across multiple AI hosts | Over-fetching data can bloat context |

---

## Guardrails concept

- Guardrails = safety rules that control what the AI can and cannot do.
- Approval gates: ask user before running destructive commands.
- Scope limits: restrict file access, network domains, or tool categories.
- Hard stops: certain actions always require explicit confirmation.
- Without guardrails, autonomous agents are too risky for production.

---

## Guardrails usage example

- File writes outside the workspace → block or require approval.
- Git push / force push → always ask for confirmation.
- Dropping tables or running migrations → hard stop, user must approve.
- External API calls → allowlist domains, block by default.
- Shell commands with rm -rf or sudo → deny automatically.

---

## Guardrails - PROS & CONS

| PROS | CONS |
|---|---|
| Prevents catastrophic mistakes | Too strict = agent cannot do its job |
| Builds trust for autonomous workflows | Hard to get the balance right |
| Required for CI/CD and production use | Needs ongoing tuning per project |
| Audit trail of approvals | Bypass paths create security holes |

---

## Observability concept

- Observability = knowing what the agent did, when, and why.
- Logs: every tool call, its input, output, and duration.
- Traces: full agent run from task start to completion.
- Metrics: success rate, token usage, cost, latency, error count.
- Without observability, debugging a failed agent run is guesswork.

---

## Observability usage example

- Log every tool call: read_file path=src/main.rs duration=120ms.
- Trace the full run: fix-bug → plan → read 3 files → edit 2 files → run tests → done.
- Metrics dashboard: tokens consumed, cost per task, error rate per tool.
- Alert: "agent made 10 tool calls but produced 0 file edits — possible loop."

---

## Observability - PROS & CONS

| PROS | CONS |
|---|---|
| Debug agent failures fast | Logging adds latency and storage cost |
| Spot loops, stalls, and drift | Sensitive data may leak into logs |
| Track cost and token usage | Needs integration into the harness |
| Improve prompts and tool defs with data | Metrics fatigue — too many dashboards |

---

## Error recovery concept

- Error recovery = what happens when a tool call fails or returns garbage.
- Retry with backoff for transient failures (network, rate limits).
- Fallback to alternative tool or strategy when primary fails.
- Escalate to user when automatic recovery is impossible.
- Dead letter: log the failure and continue with partial results.

---

## Error recovery usage example

- File read fails with ENOENT → agent asks user for correct path.
- API rate limit → exponential backoff, retry 3 times, then escalate.
- Test run times out → agent reports partial results, asks to re-run.
- Tool returns malformed JSON → agent retries with stricter prompt.
- Shell command exits non-zero → agent reads stderr, adjusts, retries once.

---

## Error recovery - PROS & CONS

| PROS | CONS |
|---|---|
| Agents survive real-world failures | Retry storms amplify load |
| Better UX — fewer user interruptions | Silent fallbacks hide real bugs |
| Essential for long-running tasks | Hard to test all failure paths |
| Reduces manual babysitting | Over-recovery can mask broken tools |

---

## Wiring diagram

User Task → Harness Engine

The Harness Engine has three core systems:
- **Guardrails** — approval gates, scope limits, hard stops
- **Orchestrator** — spawns and coordinates sub-agents
- **Observability** — logs, traces, metrics

Each sub-agent follows this pipeline:
- Prompt / Skill → MCP → Tool Defs → Error Recovery

Everything flows through **Memory / Rules** as persistent constraints, then produces the final **Output**.

Key principle: Harness is the outer shell (guard, observe, route, recover). Agent is the inner worker (plan, use tools, produce results). MCP connects everything to real tools. Memory and rules surround everything.
