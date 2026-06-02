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

## How to use

Open in browser:

```
file:///path/to/devflow/.ai/skills/md-view/viewer.html?file=.ai/agents/devflow.md
```

Or serve via any HTTP server for `fetch()` to work:

```bash
cd /path/to/devflow
python -m http.server 9090
# Open: http://localhost:9090/.ai/skills/md-view/viewer.html?file=.ai/agents/devflow.md
```

## Files

| File | Purpose |
|------|---------|
| `viewer.html` | Loads and renders any .md file via marked.js |
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
