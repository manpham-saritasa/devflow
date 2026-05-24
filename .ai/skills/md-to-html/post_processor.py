"""Card layout, responsive tables, Q&A cards, HTML wrap."""
import re
from md_parser import parse_inline

class PostProcessor:
    """Apply card-based layout, responsive tables, Q&A cards, and final HTML wrap."""

    def process(self, body_html: str, title: str, metadata: dict | None = None) -> str:
        """Run all post-processing steps."""
        body_html = body_html.replace("<br>", "")
        body_html = self._join_split_links(body_html)
        body_html = self._wrap_sections(body_html)
        body_html = self._build_header(title, metadata) + "\n" + body_html
        body_html = self._add_data_labels(body_html)
        body_html = self._wrap_qa_cards(body_html)
        return body_html

    # ── Private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _join_split_links(html: str) -> str:
        """Join links split across lines: <p>...](https</p><p>//...)</p>"""
        return re.sub(
            r"<p>(.+?)\((.+?)</p>\s*<p>(//.+?)\)</p>",
            r"<p>\1(\2\3)</p>",
            html,
            flags=re.DOTALL,
        )

    @staticmethod
    def _wrap_sections(html_body: str) -> str:
        """Wrap each h2 chunk in a section card."""
        parts = html_body.split("<h2>")
        wrapped = []
        for part in parts[1:]:
            if "</h2>" not in part:
                continue
            idx = part.index("</h2>")
            heading = part[:idx]
            rest = part[idx + 5 :].strip()
            wrapped.append(
                f'<section class="section"><h2>{heading}</h2>\n{rest}</section>'
            )
        return "\n".join(wrapped)

    @staticmethod
    def _build_header(title: str, metadata: dict | None = None) -> str:
        """Build the header card with eyebrow, h1, and metadata grid."""
        eyebrow = ""
        clean_title = title
        if ": " in title:
            parts = title.split(": ", 1)
            eyebrow = parts[0].strip()
            clean_title = parts[1].strip() if len(parts) > 1 else title

        lines = ['<section class="header">']
        if eyebrow:
            lines.append(f'  <div class="eyebrow">{eyebrow}</div>')
        lines.append(f"  <h1>{parse_inline(clean_title)}</h1>")

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

    @staticmethod
    def _add_data_labels(html_body: str) -> str:
        """Add data-label attributes to td elements based on th text."""

        def _process_table(m):
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

        return re.sub(r"<table>.*?</table>", _process_table, html_body, flags=re.DOTALL)

    @staticmethod
    def _wrap_qa_cards(html_body: str) -> str:
        """Convert Q&A pattern lists into block-card grids."""

        def _process_qa_section(m):
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
            after_heading = section[heading_match.end() :] if heading_match else section
            prefix = ""
            ul_idx = after_heading.find("<ul>")
            if ul_idx > 0:
                prefix = after_heading[:ul_idx].strip()

            grid = '<div class="block-grid">\n' + "\n".join(cards) + "\n</div>"
            prefix_block = f"{prefix}\n" if prefix else ""
            return (
                f'<section class="section">\n{heading}\n'
                f"{prefix_block}{grid}\n</section>"
            )

        return re.sub(
            r'<section class="section">\s*<h2>[^<]*Questions?[^<]*</h2>.*?</section>',
            _process_qa_section,
            html_body,
            flags=re.DOTALL,
        )


# ── Converter ───────────────────────────────────────────────────────────────


