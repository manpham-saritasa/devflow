---
name: md-view
version: 0.1.0
description: Render any Markdown file in a browser with the card-based theme. No conversion needed — open viewer.html?file=path/to/doc.md and see the rendered result instantly.
triggers:
  - "md-view"
  - "view md"
  - "preview md"
---

# md-view

Render Markdown files in-browser without conversion. One HTML file + one CSS theme. No per-file .html artifacts.

## When to use

Use when:
- You want to preview a .md file quickly without running the converter
- You're iterating on a .md file and want live-ish preview (refresh browser)
- You don't need the full md-to-html conversion (Q&A cards, example boxes, inline links)

Do not use when:
- You need a shareable, self-contained HTML file → use `md-to-html` instead
- You need all post-processing (data-labels, example boxes, `<hr>` stripping) → `md-to-html` gives richer output

## Workflow

**With a file path:**

1. Start HTTP server if not running:
```bash
cd /path/to/devflow
python -m http.server 9090 &
```

2. Present as clickable link:
```
[path/from/repo/root](http://localhost:9090/.ai/skills/md-view/viewer.html?file=[relative-path])
```

Link text shows the path relative to repo root.
- `.ai/plugins/devflow/skills/2.dev-plan/SKILL.md` → `devflow/skills/2.dev-plan/SKILL.md`
- `.local/memory.md` → `.local/memory.md`

**Without a file path:**

1. Start server if not running.
2. List recently created/edited .md files from this session as clickable links.
3. Show numbered list for easy reference:
```
1. [dev-plan.md](http://localhost:9090/...)
2. [jira-close.md](http://localhost:9090/...)
...
```

## Files

| File | Purpose |
|------|---------|
| `mdview.html` | Drag-and-drop viewer — no server needed |
| `viewer.html` | Server-based viewer — uses ?file= parameter |
| `theme.css` | Same card-based theme as md-to-html |

## What it does

- Fetches the .md file from the repo (relative to viewer.html)
- Extracts YAML frontmatter for header card
- Renders Markdown → HTML with marked.js
- Wraps sections in `.section` cards
- Converts blockquotes to `.blockquotes` cards
- Renders Mermaid diagrams

## What it doesn't do (vs md-to-html)

- No Q&A block-card grids
- No ✅/❌ example boxes
- No `data-label` attrs for responsive tables
- No `<hr>` stripping
- No inline link processing
- Not self-contained (needs CDN for marked.js + mermaid)

Use `md-to-html` when you need the full rich output. Use `md-view` for quick previews.

## Rules

- Check if server already running on first invocation. Reuse if alive.
- If port blocked, increment and retry up to 9099.
- Always present URL as clickable markdown link: `[text](url)`.
- Server stays running between invocations — don't kill it after each view.
