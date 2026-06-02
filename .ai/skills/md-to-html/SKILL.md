---
name: md-to-html
description: Convert Markdown files into polished standalone HTML files using a clean card-based layout, embedded CSS, responsive tables, and readable document styling.
triggers:
  - "md-to-html"
  - "to-html"
  - "md-html"
---

# Skill: md-to-html

## Purpose

Use this skill when the user wants to:
- Convert a Markdown file into an HTML file.
- Turn notes, reports, specs, proposals, plans, or documentation into a shareable HTML page.
- Reuse the same visual style across multiple Markdown-based documents.
- Produce a readable HTML document instead of plain Markdown.

This skill is specifically for:
- Documentation pages.
- Reports.
- Technical notes.
- Project plans.
- Internal writeups.
- Client-facing or team-facing documents.

## Output rules

- The final deliverable must be a standalone `.html` file.
- Keep the HTML self-contained, with embedded CSS in one file unless the user explicitly asks for separate assets.
- Use semantic HTML: `main`, `section`, `table`, `thead`, `tbody`, `ul`, `li`, headings in order.
- Use normal newlines in text content. Do not use `<br>` as a spacing tool.
- For lists inside table cells, use HTML list tags: `<ul><li>...</li></ul>`.
- Keep the wording simple, short, direct, and readable.
- Prefer neutral professional language unless the source content clearly calls for another tone.
- Do not include inline citations in the generated HTML file unless the user explicitly asks for them.

## Conversion behavior

- Preserve the source document structure as much as possible.
- Convert Markdown headings into proper HTML heading tags.
- Convert Markdown paragraphs into HTML paragraphs.
- Convert Markdown bullet and numbered lists into HTML lists.
- Convert Markdown tables into HTML tables.
- Convert code blocks into HTML `pre` and `code` blocks.
- Convert links into clickable HTML anchors.
- Keep section order from the source Markdown unless the user asks to restructure it.
- If the source Markdown has repeated separators or formatting noise, clean it up during conversion.
- If the source Markdown uses weak formatting that would render poorly in HTML, normalize it into cleaner HTML structure.

### Good/Bad example boxes

When the source Markdown contains paired examples using ✅ (good) and ❌ (bad) markers, wrap each in a styled example box:

- `✅ ...` items → `<div class="example-box good-box"><p>✅ ...</p></div>`
- `❌ ...` items → `<div class="example-box bad-box"><p>❌ ...</p></div>`

Group examples under their parent heading. Place each example-box as a sibling, not nested inside a list. The `p { margin: 0; }` inside `.example-box` is already handled by the theme — do not add extra margin or `<br>` inside these boxes.

### Blockquote cards

Convert `<blockquote>` elements into styled `.blockquotes` cards:

- `<blockquote><p>...</p></blockquote>` → `<div class="blockquotes"><p>...</p></div>`

Applies to all blockquotes in the document. The `p { margin: 0; }` inside `.blockquotes` is already handled by the theme.

## Writing rules

- Keep the original meaning of the Markdown file.
- Clean up formatting without changing the substance.
- Remove obvious Markdown-only artifacts when they are no longer useful in HTML.
- Keep paragraphs short when possible.
- Prefer readable spacing, tables, and lists over dense text blocks.
- Avoid unnecessary decorative elements.

## Visual format

Generate a polished HTML document with this visual approach:

### Layout
- Centered page container with a max width around 1100-1200px.
- Soft page background.
- Card-style main sections with rounded corners, thin borders, and light shadow.
- No `<hr>` separators between sections — the card layout provides visual separation.
- A top header card with the document title and optional metadata when available.
- Clear spacing between sections.

### Typography
- Clean sans-serif stack such as Inter, Segoe UI, Roboto, Arial, sans-serif.
- Strong but calm heading hierarchy.
- Slightly larger default font sizing for easier reading.
- Readable table text that is not too small by default.
- Table header font should match body font size for readability.
- Muted supporting text for secondary details.
- Comfortable line height for document reading.

### Tables
- Full-width tables.
- Light header background with readable font size.
- Very light 1px border on cells.
- Lighter even-row background (lighter than header, subtle alternation).
- On mobile, convert table rows into stacked blocks using CSS.
- Each `td` should support `data-label` for responsive display.

### Cards and blocks
- Section wrappers should look like clean document cards.
- Optional callout or question blocks can use a bordered light surface.
- Lists inside tables should render with real HTML lists.

### Colors
Use this approved palette by default:
- Page background: `#f6f7f9`
- Primary surface: `#ffffff`
- Secondary surface: `#f1f4f8`
- Main text: `#1f2937`
- Muted text: `#5b6574`
- Border: `#d9e0e7`
- Accent: `#0f766e`
- Accent soft: `#e6f4f1`
- Warning: `#9a3412`
- Shadow: `0 10px 30px rgba(15, 23, 42, 0.08)`
- Base radius: `14px`

## Approved CSS theme

Unless the user explicitly asks for a different style, read the CSS from `theme.css` at the skill root. The bundled converter script (`main.py`) automatically injects it — no manual copy needed.

To adjust the theme, edit `theme.css` directly. All HTML files regenerate from one source.

## HTML skeleton

Use this general shape:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>[Document Title]</title>
  <style>
    /* CSS injected from theme.css by the converter script */
  </style>
</head>
<body>
  <main class="page">
    <section class="header">...</section>
    <section class="section">...</section>
    <section class="section">...</section>
  </main>
</body>
</html>
```

## Usage

Install the parser dependencies first:

```bash
python -m pip install -r .ai/skills/md-to-html/requirements.txt
```

If `python` is not available on Windows, use:

```bash
py.exe -m pip install -r .ai/skills/md-to-html/requirements.txt
```

Then run the bundled converter script:

```bash
python .ai/skills/md-to-html/scripts/main.py <input.md> [output.html]
```

If `python` is not available on Windows, use:

```bash
py.exe .ai/skills/md-to-html/scripts/main.py <input.md> [output.html]
```

If `output.html` is omitted, it writes to `<input_stem>.html` alongside the source file.

The script handles everything in one pass: Markdown parsing, card-based layout, metadata extraction, heading normalization, `<br>`/`<hr>` stripping, bullet-list-in-table-cells, `data-label` attributes for responsive tables, and Q&A `block-card` grids.

## File naming

Use descriptive lowercase hyphenated filenames, for example:
- `project-plan.html`
- `technical-notes.html`
- `migration-report.html`
- `converted-document.html`
