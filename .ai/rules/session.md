# Session Tracking Rule

Every 10 minutes during a working session:

1. **Save session state** to `../../sessions/[session ID].md` with:
   - Summary of what was done
   - List of files changed
   - Key decisions made

   Example from a worktree:
   ```
   D:\devflow-worktrees\feature\key-11-enhance-more\
   └── ..\..\sessions\
       ├── 2026-05-27.md
       └── corrections.md
   ```
   Resolves to: `D:\devflow-worktrees\sessions\`

2. **Extract key corrections** and append them to `../../sessions/corrections.md` so the AI can read them on next startup.

The session folder (`../../sessions`) lives outside any single worktree so it persists across all feature branches.
