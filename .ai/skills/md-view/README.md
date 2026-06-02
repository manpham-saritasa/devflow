# md-view

Quick Markdown preview — one HTML file, one CSS theme. No conversion needed.

## Quick start (Windows)

Double-click `start.bat` or run in terminal:

```cmd
start.bat
```

Opens browser with this README rendered.

## Quick start (macOS / Linux)

```bash
cd /path/to/devflow
python3 -m http.server 9090
# Open: http://localhost:9090/.ai/skills/md-view/viewer.html
```

## View any .md file

Add `?file=` to the URL:

```
http://localhost:9090/.ai/skills/md-view/viewer.html?file=.ai/agents/devflow.md
```

## Files

| File | Purpose |
|------|---------|
| `viewer.html` | Loads and renders any .md file via marked.js |
| `theme.css` | Card-based theme (same as md-to-html) |
| `start.bat` | Windows one-click server starter |
