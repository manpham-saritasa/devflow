"""
md-to-html — Convert Markdown files into polished standalone HTML files.

Usage:
    python convert.py <input.md> [output.html]

If output.html is omitted, writes to <input_stem>.html alongside the source.
"""

import re
import sys
from pathlib import Path

from md_parser import md_body_to_html

HERE = Path(__file__).parent
CSS = (HERE / "theme.css").read_text(encoding="utf-8")


# ── Post-processing ─────────────────────────────────────────────────────────


def post_process(html_body: str, title: str, metadata: dict | None = None) -> str:
    """Apply card-based layout and all post-processing fixes."""
    html_body = html_body.replace("<br>", "")

    # Wrap each h2 chunk in a section card
    parts = html_body.split("<h2>")
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

    header_html = _build_header(title, metadata)
    body = "\n".join(section_parts)
    body = _add_data_labels(body)
    body = _wrap_qa_cards(body)
    return f"{header_html}\n{body}"


def _build_header(title: str, metadata: dict | None = None) -> str:
    """Build the header card section."""
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
            link_match = re.match(r"\[(.+?)\]\((.+?)\)", value)
            if link_match:
                display, url = link_match.groups()
                val_html = f'<a href="{url}">{display}</a>'
            else:
                val_html = value
            lines.append(
                f'    <div class="meta-item">'
                f'<span class="meta-label">{key}</span>{val_html}'
                f"</div>"
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
        rows = re.findall(r"<tr>(.*?)</tr>", table, re.DOTALL)
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
        for old_row, new_row in zip(rows, new_rows):
            table = table.replace(f"<tr>{old_row}</tr>", f"<tr>{new_row}</tr>", 1)
        return table

    return re.sub(r"<table>.*?</table>", process_table, html_body, flags=re.DOTALL)


def _wrap_qa_cards(html_body: str) -> str:
    """Convert Q&A pattern lists into block-card grids."""

    def process_qa_section(m):
        section = m.group(0)
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

        heading_match = re.search(r"(<h2>[^<]*Questions?[^<]*</h2>)", section)
        heading = heading_match.group(1) if heading_match else ""
        after_heading = section[heading_match.end():] if heading_match else section
        prefix = ""
        ul_idx = after_heading.find("<ul>")
        if ul_idx > 0:
            prefix = after_heading[:ul_idx].strip()

        grid = '<div class="block-grid">\n' + "\n".join(cards) + "\n</div>"
        prefix_block = f"{prefix}\n" if prefix else ""
        return f'<section class="section">\n{heading}\n{prefix_block}{grid}\n</section>'

    return re.sub(
        r'<section class="section">\s*<h2>[^<]*Questions?[^<]*</h2>.*?</section>',
        process_qa_section,
        html_body,
        flags=re.DOTALL,
    )


# ── Metadata extraction ─────────────────────────────────────────────────────


def parse_frontmatter(md_text: str):
    """Parse YAML-like frontmatter between --- delimiters at the top of a document.

    Returns (body_without_frontmatter, frontmatter_dict).
    Keys with list values are joined with ', ' for display.
    """
    lines = md_text.split("\n")
    if not lines:
        return md_text, {}

    # Find opening --- within first 10 lines (heading may precede it)
    start = -1
    for i in range(min(10, len(lines))):
        if lines[i].strip() == "---":
            start = i
            break
    if start == -1:
        return md_text, {}

    # Find closing ---
    end = -1
    for i in range(start + 1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end == -1:
        return md_text, {}

    fm: dict[str, str] = {}
    current_key = ""
    for line in lines[start + 1 : end]:
        stripped = line.strip()
        if not stripped:
            continue
        # List item:   - value  or  - "value"
        m = re.match(r'^\s*-\s*(?:"(.+?)"|(.+))\s*$', line)
        if m and current_key:
            item = m.group(1) or m.group(2)
            existing = fm.get(current_key, "")
            fm[current_key] = existing + (", " if existing else "") + item.strip()
            continue
        # Key with value:  key: value
        m = re.match(r"^([\w-]+):\s+(.+)$", stripped)
        if m:
            current_key = m.group(1)
            fm[current_key] = m.group(2).strip()
            continue
        # Key without value:  key:
        m = re.match(r"^([\w-]+):\s*$", stripped)
        if m:
            current_key = m.group(1)
            fm[current_key] = ""

    body = "\n".join(lines[:start] + lines[end + 1 :])
    return body, fm


def extract_metadata(md_text: str) -> tuple[str, dict]:
    """Extract title and metadata key-value pairs from the header block.

    Stops at the first HR (*** or ---).
    """
    lines = md_text.split("\n")
    title = ""
    metadata = {}

    for line in lines:
        stripped = line.strip()
        if re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", stripped):
            break
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
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

    body_text, frontmatter = parse_frontmatter(md_text)
    title, metadata = extract_metadata(body_text)
    if not title:
        title = md_path.stem.replace("-", " ").title()

    meta = {**metadata, **frontmatter}
    body_html = md_body_to_html(body_text)
    final_body = post_process(body_html, title, meta)

    mermaid_script = ""
    if 'class="mermaid"' in final_body:
        mermaid_script = (
            '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js">'
            '</script>\n'
            '<script>mermaid.initialize({startOnLoad:true,theme:"default"});</script>'
        )

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
{mermaid_script}
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

    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else md_path.with_suffix(".html")
    result = convert(md_path, out_path)
    print(f"HTML written to {result} ({result.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
