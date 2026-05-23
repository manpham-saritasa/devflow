"""
md-to-html — Convert Markdown files into polished standalone HTML files.

Usage:
    python convert.py <input.md> [output.html]

If output.html is omitted, writes to <input_stem>.html alongside the source.
"""

import re
import sys
from pathlib import Path

# ── Approved CSS theme (from SKILL.md) ──────────────────────────────────────

CSS = """\
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
  --radius: 9px;
  --title: #1e3a5f;
  --table-even-row: #f8fafc;
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
  border-radius: 9px;
  box-shadow: var(--shadow);
  padding: 28px;
  margin-bottom: 24px;
  overflow: hidden;
}
.eyebrow {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 9px;
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
  color: var(--title);
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
  border-radius: 9px;
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
  border-radius: 9px;
  box-shadow: var(--shadow);
  padding: 24px;
  margin-bottom: 20px;
  overflow: hidden;
}
h2 {
  margin: 0 0 16px;
  font-size: 28px;
  color: var(--title);
}
h3 {
  margin: 24px 0 10px;
  font-size: 20px;
  color: var(--title);
}
h4 {
  color: var(--title);
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
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid var(--table-border);
  border-radius: 9px;
  overflow: hidden;
  background: #fff;
}
th, td {
  border-bottom: 1px solid var(--table-border);
  border-right: 1px solid var(--table-border);
  vertical-align: top;
  text-align: left;
  padding: 16px 16px;
  font-size: 15px;
}
th {
  background: #e6f4f8;
  font-size: 15px;
  color: var(--title);
}
tr:last-child td,
tr:last-child th {
  border-bottom: none;
}
td:last-child,
th:last-child {
  border-right: none;
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
  border-radius: 9px;
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
  border-radius: 9px;
}
.block-card {
  border: 1px solid var(--border);
  background: #fbfcfd;
  border-radius: 9px;
  padding: 14px 16px;
  overflow: hidden;
}
.block-grid {
  display: grid;
  gap: 14px;
}
.q { font-weight: 700; margin: 0 0 8px; color: var(--text); }
.a { color: var(--muted); margin: 0; }
strong, h2, h3, h4 { color: var(--title); }
a, h1 { color: var(--accent); text-decoration: none; }
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
}"""


# ── Markdown → HTML body converter ──────────────────────────────────────────


def md_body_to_html(text: str) -> str:
    """Convert Markdown body text to flat HTML (no page wrapper)."""
    lines = text.split("\n")
    out = []
    i = 0

    def emit(s):
        out.append(s)

    def parse_inline(t):
        # bold
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        # inline code
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        # links
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
        # italic
        t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
        return t

    in_table = False
    in_list = False
    in_code_block = False
    code_buf = []
    list_tag = "ul"
    table_header_done = False

    def close_table():
        nonlocal in_table, table_header_done
        if in_table:
            emit("</tbody></table>")
            in_table = False
            table_header_done = False

    while i < len(lines):
        line = lines[i]

        # code block (fenced)
        if line.strip().startswith("```"):
            if in_code_block:
                emit(f"<pre><code>{''.join(code_buf).rstrip()}</code></pre>")
                code_buf = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_buf.append(line + "\n")
            i += 1
            continue

        # empty line
        if line.strip() == "":
            if in_list:
                emit(f"</{list_tag}>")
                in_list = False
            i += 1
            continue

        # HR
        if re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", line.strip()):
            close_table()
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            close_table()
            if in_list:
                emit(f"</{list_tag}>")
                in_list = False
            level = len(m.group(1))
            # Normalize to h3 max (h4→h3 per skill post-processing rules)
            if level > 3:
                level = 3
            content = parse_inline(m.group(2))
            emit(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # table separator row
        if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
            if in_table:
                table_header_done = True
            i += 1
            continue

        # table row
        if line.strip().startswith("|") and line.strip().endswith("|"):
            if not in_table:
                in_table = True
                table_header_done = False
                emit("<table><thead>")
            if not table_header_done:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                emit("<tr>")
                for c in cells:
                    emit(f"<th>{parse_inline(c)}</th>")
                emit("</tr>")
                emit("</thead><tbody>")
                table_header_done = True
            else:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                emit("<tr>")
                for c in cells:
                    # check for embedded list markers in cell
                    c_html = parse_inline(c)
                    # If cell contains bullet markers, convert to ul
                    if "<br>" in c_html or re.search(r"(?:^|\s)-\s", c):
                        # Split on <br> or newline-like patterns and handle bullets
                        c_html = _cell_to_list(c_html)
                    emit(f"<td>{c_html}</td>")
                emit("</tr>")
            i += 1
            continue
        else:
            close_table()

        # unordered list item
        m = re.match(r"^(\s*)[-*]\s+(.+)$", line)
        if m:
            if not in_list:
                in_list = True
                list_tag = "ul"
                emit("<ul>")
            content = parse_inline(m.group(2))
            # peek ahead for continuation lines
            j = i + 1
            while (
                j < len(lines)
                and lines[j].strip()
                and not re.match(r"^(\s*)[-*]\s+", lines[j])
                and not re.match(r"^\s*\d+\.\s+", lines[j])
                and not lines[j].strip().startswith("#")
                and not re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", lines[j].strip())
                and not lines[j].strip().startswith("|")
                and not lines[j].strip().startswith("```")
            ):
                content += "<br>" + parse_inline(lines[j].strip())
                j += 1
            emit(f"<li>{content}</li>")
            i = j
            continue

        # ordered list item
        m = re.match(r"^(\s*)\d+\.\s+(.+)$", line)
        if m:
            if not in_list:
                in_list = True
                list_tag = "ol"
                emit("<ol>")
            content = parse_inline(m.group(2))
            emit(f"<li>{content}</li>")
            i += 1
            continue

        # paragraph
        content = parse_inline(line.strip())
        if content:
            emit(f"<p>{content}</p>")
        i += 1

    # close open blocks
    if in_list:
        emit(f"</{list_tag}>")
    if in_table:
        emit("</tbody></table>")

    return "\n".join(out)


def _cell_to_list(cell_html: str) -> str:
    """Convert <br>-separated bullet items in a table cell to <ul><li>."""
    # Split on <br>
    parts = cell_html.split("<br>")
    # Trim whitespace from each part
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        return cell_html
    # Check if most parts start with bullet markers
    bullet_count = sum(1 for p in parts if re.match(r"^[-*]\s", p))
    if bullet_count >= len(parts) * 0.5:
        items = [re.sub(r"^[-*]\s+", "", p) for p in parts]
        return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"
    return cell_html


# ── Post-processing (from SKILL.md) ─────────────────────────────────────────


def post_process(html_body: str, title: str, metadata: dict | None = None) -> str:
    """Apply card-based layout and all post-processing fixes."""

    # Step 1: Strip any <br> from source (skill rule)
    html_body = html_body.replace("<br>", "")

    # Step 2: Wrap in header card + section cards
    # Split by <h2>
    parts = html_body.split("<h2>")
    header_content = parts[0].strip()
    section_parts = []
    for part in parts[1:]:
        if "</h2>" not in part:
            continue
        idx = part.index("</h2>")
        heading = part[:idx]
        rest = part[idx + 5 :]
        section_parts.append(
            f'<section class="section"><h2>{heading}</h2>\n{rest.strip()}</section>'
        )

    # Step 3: Build header card
    header_html = _build_header(title, metadata)

    # Step 4: Add data-label attributes to td elements
    body_with_sections = "\n".join(section_parts)
    body_with_sections = _add_data_labels(body_with_sections)

    # Step 5: Convert Q&A lists to card blocks
    body_with_sections = _wrap_qa_cards(body_with_sections)

    return f"{header_html}\n{body_with_sections}"


def _build_header(title: str, metadata: dict | None = None) -> str:
    """Build the header card section."""
    # Extract eyebrow if present (e.g., "ADR:" prefix)
    eyebrow = ""
    clean_title = title
    if ":" in title:
        parts = title.split(":", 1)
        eyebrow = parts[0].strip()
        clean_title = parts[1].strip() if len(parts) > 1 else title

    lines = ['<section class="header">']
    if eyebrow:
        lines.append(f'  <div class="eyebrow">{eyebrow}</div>')
    lines.append(f"  <h1>{clean_title}</h1>")

    if metadata:
        lines.append('  <div class="meta">')
        for key, value in metadata.items():
            # Detect links in value
            link_match = re.match(r"\[(.+?)\]\((.+?)\)", value)
            if link_match:
                display, url = link_match.groups()
                val_html = f'<a href="{url}">{display}</a>'
            else:
                val_html = value
            lines.append(
                f'    <div class="meta-item"><span class="meta-label">{key}</span>{val_html}</div>'
            )
        lines.append("  </div>")

    lines.append("</section>")
    return "\n".join(lines)


def _add_data_labels(html_body: str) -> str:
    """Add data-label attributes to td elements based on th text."""

    def process_table(m):
        table = m.group(0)
        headers = re.findall(r"<th>(.+?)</th>", table)
        if not headers:
            return table
        clean_headers = [re.sub(r"<.*?>", "", h).strip() for h in headers]
        # Replace each <td> in sequence with matching data-label
        result = table
        # Build rows back: for each row, assign labels
        rows = re.findall(r"<tr>(.*?)</tr>", result, re.DOTALL)
        new_rows = []
        for row_html in rows:
            if "<th>" in row_html:
                new_rows.append(row_html)
                continue
            tds = re.findall(r"<td>(.*?)</td>", row_html, re.DOTALL)
            new_row = row_html
            for j, td_content in enumerate(tds):
                if j < len(clean_headers):
                    label = clean_headers[j]
                    old = f"<td>{td_content}</td>"
                    new = f'<td data-label="{label}">{td_content}</td>'
                    new_row = new_row.replace(old, new, 1)
            new_rows.append(new_row)
        # Rebuild table
        for old_row, new_row in zip(rows, new_rows):
            result = result.replace(f"<tr>{old_row}</tr>", f"<tr>{new_row}</tr>", 1)
        return result

    return re.sub(r"<table>.*?</table>", process_table, html_body, flags=re.DOTALL)


def _wrap_qa_cards(html_body: str) -> str:
    """Convert Q&A pattern lists into block-card grids."""

    def process_qa_section(m):
        section = m.group(0)
        # Replace all <ul>...</ul> with cards, wrap in single block-grid
        # First, extract all <li> content
        all_items = re.findall(r"<li>(.*?)</li>", section, re.DOTALL)
        if not all_items:
            return section

        cards = []
        for inner in all_items:
            q_match = re.search(r"(<strong>Q\d+:.*?)<strong>A", inner, re.DOTALL)
            if q_match:
                q_content = q_match.group(1).strip()
                a_content = inner[q_match.end() - len("<strong>A") :].strip()
                q_content = re.sub(r"^<p>|</p>$", "", q_content).strip()
                a_content = re.sub(r"^<p>|</p>$", "", a_content).strip()
                cards.append(
                    f'<div class="block-card">'
                    f'<p class="q">{q_content}</p>'
                    f'<p class="a">{a_content}</p>'
                    f"</div>"
                )

        if not cards:
            return section

        # Build replacement: keep heading, replace list area with single block-grid
        heading_match = re.search(r"(<h2>[^<]*Questions?[^<]*</h2>)", section)
        heading = heading_match.group(1) if heading_match else ""
        grid = '<div class="block-grid">\n' + "\n".join(cards) + "\n</div>"
        return f'<section class="section">\n{heading}\n{grid}\n</section>'

    # Find sections containing Open Questions (or similar QA sections)
    return re.sub(
        r'<section class="section">\s*<h2>[^<]*Questions?[^<]*</h2>.*?</section>',
        process_qa_section,
        html_body,
        flags=re.DOTALL,
    )


# ── Metadata extraction ─────────────────────────────────────────────────────


def extract_metadata(md_text: str) -> tuple[str, dict]:
    """Extract title and metadata key-value pairs from ADR-style Markdown.

    Only scans the header block — stops at the first HR (*** or ---).
    """
    lines = md_text.split("\n")
    title = ""
    metadata = {}

    for line in lines:
        stripped = line.strip()
        # Stop at first HR — metadata only lives in the header
        if re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", stripped):
            break
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
        # **Key:** value pattern
        m = re.match(r"^\*\*(.+?):\*\*\s+(.+)$", stripped)
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()
            metadata[key] = value

    return title, metadata


# ── Main ─────────────────────────────────────────────────────────────────────


def convert(md_path: Path, out_path: Path) -> Path:
    """Convert a Markdown file to HTML using the md-to-html skill rules."""
    md_text = md_path.read_text(encoding="utf-8")

    title, metadata = extract_metadata(md_text)
    if not title:
        title = md_path.stem.replace("-", " ").title()

    body_html = md_body_to_html(md_text)
    final_body = post_process(body_html, title, metadata)

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
{CSS}
  </style>
</head>
<body>
  <main class="page">
{final_body}
  </main>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert.py <input.md> [output.html]")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"Error: file not found: {md_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])
    else:
        out_path = md_path.with_suffix(".html")

    result = convert(md_path, out_path)
    print(f"HTML written to {result} ({result.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
