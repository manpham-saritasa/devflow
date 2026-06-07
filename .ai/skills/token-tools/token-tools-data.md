# Token Tool Catalog

Quick-reference catalog for `token-tools` skill. Dev-side tools only — ranked by independent benchmark results where available.

**Format:** Each tool has: URL, What, Token savings, Agents, Zed supported, OS, Install, Difficulty.

---

## Token saving

### 1) token-savior — MCP server, structural + bash compaction

- URL: [Mibayy/token-savior](https://github.com/Mibayy/token-savior)
- Stars: 955
- Benchmark: 🥇 -43% token reduction (leaderboard), -80% on tsbench (96 tasks)
- What: MCP server with structural code navigation (symbol index), persistent memory (SQLite), and 34 bash output compactors. Proactive tool use reduction.
- Token savings: High (benchmark-verified, 97.9% tsbench score)
- Agents: Claude Code, Cursor, Gemini, Codex (MCP-compatible)
- **Zed supported: No** (MCP-only, Zed doesn't support MCP yet)
- OS: macOS, Linux, Windows
- Install:
  - `pip install "token-savior-recall[mcp]"`
  - `uvx token-savior-recall`
- Difficulty: Medium

### 2) claude-token-efficient — one-file drop-in response compression

- URL: [drona23/claude-token-efficient](https://github.com/drona23/claude-token-efficient)
- Stars: 5.5k
- Benchmark: 🥈 -40% token reduction
- What: Single CLAUDE.md file that keeps responses terse. 63% word reduction across benchmarks. Drop-in, no code changes. Multiple profiles (coding, agents, analysis).
- Token savings: ~63% output reduction, ~40% total
- Agents: Claude Code primary. Model-agnostic rules.
- **Zed supported: Yes** (prompt-configurable)
- OS: Cross-platform (config file)
- Install:
  - `curl -o CLAUDE.md https://raw.githubusercontent.com/drona23/claude-token-efficient/main/CLAUDE.md`
- Difficulty: Easy

### 3) token-optimizer — full-spectrum optimization platform

- URL: [alexgreensh/token-optimizer](https://github.com/alexgreensh/token-optimizer)
- Stars: 1.3k
- Benchmark: 🥉 -18% token reduction (but covers structural + runtime + behavioral waste)
- What: Comprehensive optimization platform. Dashboard with per-turn costs, quality scoring (v6), smart compaction with checkpoint/restore, 16 bash handlers, loop detection, delta mode, coach mode, memory health audit.
- Token savings: Measured via local telemetry (before/after tokens per feature)
- Agents: Claude Code, Codex, OpenCode, OpenClaw
- **Zed supported: No**
- OS: macOS, Linux, Windows
- Install:
  - `/plugin marketplace add alexgreensh/token-optimizer`
  - `/plugin install token-optimizer@alexgreensh-token-optimizer`
- Difficulty: Medium

### 4) RTK — transparent CLI proxy

- URL: [rtk-ai/rtk](https://github.com/rtk-ai/rtk)
- What: Compresses shell output (git diff, test runs) before it reaches the LLM.
- Token savings: 60-90% on shell output
- Agents: Claude Code, Cursor, Copilot, Gemini CLI, Windsurf, Cline, Roo Code
- **Zed supported: No**
- OS: macOS, Linux. Windows via WSL.
- Install:
  - `brew install rtk`
  - `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh`
- Difficulty: Easy

### 5) Caveman — response style compression

- URL: [JuliusBrussee/caveman](https://github.com/juliusbrussee/caveman)
- What: Cuts LLM output tokens by dropping filler, articles, pleasantries. Keeps technical accuracy.
- Token savings: ~75%
- Agents: Any prompt-configurable agent
- **Zed supported: Yes**
- OS: Cross-platform (prompt/skill config)
- Install: Add skill to agent. Already available in devflow.
- Difficulty: Easy

---

## Codebase context

### 6) Repomix — pack repo into single file

- URL: [yamadashy/repomix](https://github.com/yamadashy/repomix)
- Stars: 26.1k
- What: Packs entire repository into one AI-friendly file (XML/MD/JSON). Token counting, git-aware ignore, compression.
- Token savings: Significant (avoids repeated file reads by pre-packing context)
- Agents: Any LLM (Claude, ChatGPT, Gemini). MCP server integration.
- **Zed supported: Yes** (MCP server mode)
- OS: macOS, Linux, Windows. Also Docker, browser extension, VSCode.
- Install:
  - `npm install -g repomix`
  - `brew install repomix`
  - `npx repomix@latest`
- Difficulty: Easy

### 7) Gitingest — turn repo into prompt text

- URL: [coderamp-labs/gitingest](https://github.com/coderamp-labs/gitingest)
- Stars: 14.8k
- What: Turn any git repo into a prompt-friendly text digest for LLMs. Replace `hub` with `ingest` in any GitHub URL.
- Token savings: Significant (digest format, token counting)
- Agents: Any LLM
- **Zed supported: Yes** (CLI + Python package)
- OS: macOS, Linux, Windows
- Install:
  - `pip install gitingest`
  - `pipx install gitingest`
  - Or just: replace `github.com` with `gitingest.com` in any URL
- Difficulty: Easy

### 8) codebase-memory-mcp — code knowledge graph

- URL: [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)
- What: Builds persistent code knowledge graph. Agent queries symbols, call chains, ADRs instead of re-reading full files.
- Token savings: Significant (avoids repeated file reads)
- Agents: Claude Code, Codex CLI, Gemini CLI, Zed, OpenCode, Aider
- **Zed supported: Yes** (MCP)
- OS: macOS, Linux
- Install:
  - `curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash`
  - `codebase-memory-mcp install`
- Difficulty: Medium

---

## Session memory

### 9) claude-mem — persistent session memory

- URL: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- What: Persistent context across sessions via MCP. Token-efficient filtering before fetching.
- Token savings: Significant (no re-loading full context each session)
- Agents: Claude Code, Gemini CLI, OpenCode
- **Zed supported: No**
- OS: Cross-platform (Node/npm)
- Install:
  - `npx claude-mem install`
  - `npx claude-mem install --ide gemini-cli`
- Difficulty: Easy

---

## Quick reference

| Category | Best pick | Stars | Zed? | Benchmark |
|----------|-----------|:-----:|:---:|:---:|
| Token saving (MCP) | token-savior | 955 | ❌ | 🥇 -43% |
| Response compression | claude-token-efficient | 5.5k | ✅ | 🥈 -40% |
| Full optimization | token-optimizer | 1.3k | ❌ | 🥉 -18% |
| Shell output compression | RTK | — | ❌ | — |
| Response style | Caveman | — | ✅ | — |
| Codebase context | Repomix | 26.1k | ✅ | — |
| Codebase context | Gitingest | 14.8k | ✅ | — |
| Codebase graph | codebase-memory-mcp | — | ✅ | — |
| Session memory | claude-mem | — | ❌ | — |

### Zed users

4 tools work with Zed today:

1. **Caveman** — response compression. Already active.
2. **claude-token-efficient** — one-file CLAUDE.md for terse responses.
3. **Repomix** — pack repo for context. `npx repomix@latest`
4. **Gitingest** — digest for prompts. `pip install gitingest`
