# Skill: md-to-html

---
name: md-to-html
description: Convert Markdown files into polished standalone HTML files using a clean card-based layout, embedded CSS, responsive tables, and readable document styling.
---

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

Unless the user explicitly asks for a different style, reuse this CSS baseline directly and adjust only minor values if needed:

```css
:root {
  --bg: #f6f7f9;
  --surface: #ffffff;
  --surface-2: #f1f4f8;
  --text: #1f2937;
  --muted: #5b6574;
  --border: #d9e0e7;
  --accent: #0f766e;
  --accent-soft: #e6f4f1;
  --warning: #9a3412;
  --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  --radius: 14px;
  --table-even-row: #f7f8f9;
  --table-border: #e5e7eb;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif;
  font-size: 17px;
  color: var(--text);
  background: var(--bg);
  line-height: 1.65;
}
.page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px 56px;
}
.header {
  background: linear-gradient(180deg, #ffffff 0%, #f7fbfb 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow);
  padding: 28px;
  margin-bottom: 24px;
}
.eyebrow {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
h1 {
  margin: 0 0 10px;
  font-size: 38px;
  line-height: 1.15;
  color: var(--accent);
}
.meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 18px;
}
.meta-item {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
}
.meta-label {
  display: block;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
  margin-bottom: 4px;
  font-weight: 700;
}
.section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow);
  padding: 24px;
  margin-bottom: 20px;
}
h2 {
  margin: 0 0 16px;
  font-size: 28px;
  color: var(--accent);
}
h3 {
  margin: 24px 0 10px;
  font-size: 20px;
}
p.note {
  margin: 0 0 14px;
  color: var(--muted);
}
ul.clean {
  margin: 0;
  padding-left: 20px;
}
ul.clean li { margin: 6px 0; }
table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid var(--table-border);
  background: #fff;
}
th, td {
  border: 1px solid var(--table-border);
  vertical-align: top;
  text-align: left;
  padding: 16px 16px;
  font-size: 15px;
}
th {
  background: #f8fafc;
  font-size: 15px;
  color: #334155;
}
tbody tr:nth-child(even) td { background: var(--table-even-row); }
td ul {
  margin: 0;
  padding-left: 18px;
}
td li { margin: 4px 0; }
pre {
  margin: 0;
  padding: 16px;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #0f172a;
  color: #e5eefc;
}
code {
  font-family: "Cascadia Code", "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}
pre code {
  color: inherit;
  background: transparent;
  padding: 0;
}
p code, li code, td code {
  background: #eef3f7;
  padding: 2px 6px;
  border-radius: 6px;
}
.block-card {
  border: 1px solid var(--border);
  background: #fbfcfd;
  border-radius: 12px;
  padding: 14px 16px;
}
.block-grid {
  display: grid;
  gap: 14px;
}
.q { font-weight: 700; margin: 0 0 8px; color: var(--text); }
.a { color: var(--muted); margin: 0; }
a, strong, h1, h2 { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
@media (max-width: 760px) {
  .page { padding: 18px 12px 36px; }
  .header, .section { padding: 16px; }
  h1 { font-size: 32px; }
  h2 { font-size: 24px; }
  table, thead, tbody, th, td, tr { display: block; }
  thead { display: none; }
  tr {
    border: 1px solid var(--table-border);
    padding: 10px 0;
  }
  td {
    border: none;
    padding: 8px 0;
  }
  td::before {
    content: attr(data-label);
    display: block;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
  }
}
```

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
    /* use the approved CSS theme */
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

## Conversion workflow

1. Read the source Markdown file.
2. Identify the document title and major sections.
3. Convert the Markdown structure into clean semantic HTML.
4. Wrap the document in the approved HTML layout and CSS theme.
5. Make sure lists inside tables use `<ul><li>`.
6. Make sure there is no `<br>` used for layout spacing.
7. Share the generated HTML file with the user.

## Post-processing fixes

Apply these after converting Markdown to HTML body. A Markdown library produces flat HTML — these steps turn it into the card-based layout.

### Strip `<br>` from source

Markdown libraries pass `<br>` through from source verbatim. Strip them before conversion:
```
body_md = body_md.replace('<br>', '')
```

### Strip `<hr>` separators

Card sections already provide visual separation. Remove all `<hr />` tags from the HTML body:
```
html_body = html_body.replace('<hr />', '')
```

### Wrap sections in cards

Split HTML by `<h2>` and wrap each chunk in `<section class="section">`. The first chunk (before first heading) is usually empty.
```python
parts = html_body.split('<h2>')
for i, part in enumerate(parts):
    if i == 0: continue
    idx = part.index('</h2>')
    heading = part[:idx + 5]
    rest = part[idx + 5:]
    wrapped_parts.append(f'<section class="section"><h2>{heading}\n{rest}</section>')
```

### Add `data-label` to table cells

Extract `<th>` text, then assign each `<td>` a matching `data-label` for responsive mobile stacking.
```python
def add_data_labels(html):
    def process_table(m):
        table = m.group(0)
        headers = re.findall(r'<th>(.+?)</th>', table)
        for h in headers:
            label = re.sub(r'<.*?>', '', h).strip()
            table = table.replace('<td>', f'<td data-label="{label}">', 1)
        return table
    return re.sub(r'<table>.*?</table>', process_table, html, flags=re.DOTALL)
```

### Normalize heading levels

Markdown `####` becomes `<h4>`, but the CSS only styles up to `<h3>`. Convert them:
```
html_body = html_body.replace('<h4>', '<h3>').replace('</h4>', '</h3>')
```

### Convert Q&A lists to card blocks

If source uses `**Q1:**` / `**A1:**` patterns inside a list, convert `<ul><li>` to cards.

First, replace the section's `<ul>` with `<div class="block-grid">`. Then replace each `<li>` that starts with `<strong>Q` with a card wrapper: `<div class="block-card"><p class="q">` and split the content at the answer marker (e.g. `<strong>A1:</strong>`) into `.q` and `.a` paragraphs.

Markdown lib may or may not wrap in `<p>` inside `<li>` depending on source formatting — handle both cases.

Concrete implementation:

```python
# Replace outer <ul> with block-grid
html_body = html_body.replace(
    '<h2>9. Open Questions</h2>\n<ul>',
    '<h2>9. Open Questions</h2>\n<div class="block-grid">'
)
html_body = html_body.replace('</ul>', '</div>')

# Wrap each Q item in a card
# Handles both: <li><strong>Q1:...  and  <li>\n<p><strong>Q1:...</p>\n</li>
def wrap_qa(m):
    raw = m.group(1)
    q_match = re.search(r'(<strong>Q\d+:.*?)<strong>A', raw, re.DOTALL)
    if q_match:
        q = re.sub(r'^<p>|</p>$', '', q_match.group(1)).strip()
        a = re.sub(r'^.*?<strong>A\d+:.*?</strong>\s*', '', raw, flags=re.DOTALL)
        a = re.sub(r'^<p>|</p>$', '', a).strip()
        return f'<div class="block-card"><p class="q">{q}</p><p class="a">{a}</p></div>'
    return m.group(0)

html_body = re.sub(
    r'<li>(?:\n)?(?:<p>)?(<strong>Q\d+:.*?<strong>A\d+:.*?)(?:</p>)?(?:\n)?</li>',
    wrap_qa,
    html_body,
    flags=re.DOTALL
)
```

## File naming

Use descriptive lowercase hyphenated filenames, for example:
- `project-plan.html`
- `technical-notes.html`
- `migration-report.html`
- `converted-document.html`

## Reusable prompt block

When this skill is used, follow this instruction pattern:

> Convert the provided Markdown file into a standalone HTML document using the approved clean document styling. Use the exact approved CSS theme unless a different visual style is requested. Preserve headings, paragraphs, lists, tables, links, and code blocks. Use section cards, responsive tables, and HTML unordered lists inside table cells where needed. Keep the language clean and readable. Do not use `<br>` for layout. Do not include citations in the HTML file unless explicitly requested.
