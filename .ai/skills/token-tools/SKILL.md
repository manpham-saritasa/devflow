---
name: token-tools
version: 0.2.0
description: Help team members choose token-saving, context-management, and context-rot mitigation tools based on OS, agent, LLM family, and hosting preference. Can install the chosen tool with OS-specific scripts.
triggers:
  - "token tools"
  - "token-tools"
  - "token advisor"
  - "save tokens"
  - "reduce tokens"
  - "install rtk"
  - "install token tool"
  - "setup token tool"
---

# Token Tool Advisor

Help team members choose and install the right token-saving tool for their setup.

## Data source

**Always read `token-tools-data.md` first** — it contains the full catalog with tool details, OS support, and install scripts.

## Workflow

### Step 1: Ask setup questions

Ask these one at a time or as a compact checklist:

1. What OS: Windows, macOS, Linux, or WSL?
2. Which coding tool: Claude Code, Cursor, Copilot, Gemini CLI, Codex CLI, Windsurf, Cline, or another?
3. Which model family: Claude, GPT/OpenAI, Gemini, or local open-source?
4. Self-hosted only, or managed SaaS ok?
5. Main pain point: token cost, slow context loading, long-session memory, or codebase navigation?
6. Fastest install, or strongest long-term architecture?

### Step 2: Recommend tools

**Show a compact summary first.** Don't dump full tool details immediately. Format:

```
## Found [N] tools for [OS] + [Agent] + [problem]

| # | Tool | Category | Zed? | Install |
|---|------|----------|:---:|---------|
| 1 | RTK | Token saving | ❌ | `brew install rtk` |

See details? (yes / show me specifics)
```

Wait for user to confirm before showing full tool descriptions with install scripts.

Use these decision rules to filter `token-tools-data.md`:

- Claude Code / Cursor + immediate savings → recommend **RTK**.
- Repeated file reads / large codebase → recommend **codebase-memory-mcp**.
- Persistent session memory, MCP workflow → recommend **claude-mem**.
- Application-level memory / context rot → recommend **Redis** or **Milvus**.
- SaaS ok, less infra → include **Supermemory**.

Present 2-3 primary picks + 1 optional advanced tool. For each:

- Tool name + category
- GitHub URL
- OS support
- Installation difficulty
- Why it fits their setup

### Step 3: Offer install

After listing recommendations:

```
❓ Which tool do you want me to install? Or say "all" for all recommendations.
```

When user picks a tool, look up the install command in `token-tools-data.md` and show the exact OS-specific commands to run.

## Output style

- Tables preferred over bullet lists for tool comparison.
- Show install commands as copy-paste-ready code blocks.
- Prefer tools already compatible with their existing editor/agent.
- Avoid SaaS if user said self-hosted only.
