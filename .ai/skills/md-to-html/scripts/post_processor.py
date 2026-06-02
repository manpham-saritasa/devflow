"""Card layout, responsive tables, Q&A cards, HTML wrap."""

from __future__ import annotations

import html
import re

from md_parser import parse_inline


class PostProcessor:
    """Apply card-based layout, responsive tables, Q&A cards, and final HTML wrap."""

    def process(
        self, body_html: str, title: str, metadata: dict[str, str] | None = None
    ) -> str:
        """Run all post-processing steps."""
        body_html = self._strip_duplicate_title_heading(body_html, title)
        body_html = self._strip_horizontal_rules(body_html)
        body_html = self._wrap_sections(body_html)
        body_html = self._build_header(title, metadata) + "\n" + body_html
        body_html = self._add_data_labels(body_html)
        body_html = self._wrap_qa_cards(body_html)
        body_html = self._wrap_example_boxes(body_html)
        body_html = self._wrap_blockquotes(body_html)
        body_html = self._add_blank_target(body_html)
        return body_html

    @staticmethod
    def _strip_duplicate_title_heading(html_body: str, title: str) -> str:
        """Remove the first body h1 when it duplicates the rendered header title."""
        title_html = parse_inline(title).strip()
        pattern = rf"^\s*<h1>{re.escape(title_html)}</h1>\s*"
        return re.sub(pattern, "", html_body, count=1)

    @staticmethod
    def _strip_horizontal_rules(html_body: str) -> str:
        """Remove markdown separator rules; card layout already separates sections."""
        return re.sub(r"\s*<hr\s*/?>\s*", "\n", html_body, flags=re.IGNORECASE)

    @staticmethod
    def _wrap_sections(html_body: str) -> str:
        """Wrap document chunks in card sections while preserving intro content."""
        html_body = html_body.strip()
        if not html_body:
            return ""

        chunks = re.split(r"(?=<h2(?:\s|>))", html_body)
        wrapped: list[str] = []

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            wrapped.append(f'<section class="section">\n{chunk}\n</section>')

        return "\n".join(wrapped)

    @staticmethod
    def _build_header(title: str, metadata: dict[str, str] | None = None) -> str:
        """Build the header card with eyebrow, h1, and metadata grid."""
        eyebrow = ""
        clean_title = title
        if ": " in title and "http://" not in title and "https://" not in title:
            parts = title.split(": ", 1)
            eyebrow = parts[0].strip()
            clean_title = parts[1].strip() if len(parts) > 1 else title

        lines = ['<section class="header">']
        if eyebrow:
            lines.append(f'  <div class="eyebrow">{html.escape(eyebrow)}</div>')
        lines.append(f"  <h1>{parse_inline(clean_title)}</h1>")

        if metadata:
            lines.append('  <div class="meta">')
            for key, value in metadata.items():
                val_html = parse_inline(value) if value else ""
                lines.append(
                    f'    <div class="meta-item">'
                    f'<span class="meta-label">{html.escape(str(key))}</span>{val_html}'
                    f"</div>"
                )
            lines.append("  </div>")

        lines.append("</section>")
        return "\n".join(lines)

    @staticmethod
    def _add_data_labels(html_body: str) -> str:
        """Add data-label attributes to td elements based on th text."""

        def _process_table(match: re.Match[str]) -> str:
            table = match.group(0)
            headers = re.findall(r"<th>(.+?)</th>", table, re.DOTALL)
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
                for index, td_content in enumerate(tds):
                    if index < len(clean_headers):
                        label = html.escape(clean_headers[index], quote=True)
                        normalized_content = (
                            PostProcessor._normalize_table_cell_content(td_content)
                        )
                        old = f"<td>{td_content}</td>"
                        new = f'<td data-label="{label}">{normalized_content}</td>'
                        new_row = new_row.replace(old, new, 1)
                new_rows.append(new_row)
            for old_row, new_row in zip(rows, new_rows):
                table = table.replace(f"<tr>{old_row}</tr>", f"<tr>{new_row}</tr>", 1)
            return table

        return re.sub(r"<table>.*?</table>", _process_table, html_body, flags=re.DOTALL)

    @staticmethod
    def _normalize_table_cell_content(td_content: str) -> str:
        """Convert bullet-like line breaks inside table cells back into real HTML lists."""
        parts = [
            part.strip() for part in re.split(r"<br\s*/?>", td_content) if part.strip()
        ]
        if len(parts) < 2:
            return td_content

        bullet_items: list[str] = []
        for part in parts:
            match = re.match(r"^[-*•]\s+(.+)$", part, flags=re.DOTALL)
            if not match:
                return td_content
            bullet_items.append(match.group(1).strip())

        return "<ul>" + "".join(f"<li>{item}</li>" for item in bullet_items) + "</ul>"

    @staticmethod
    def _wrap_qa_cards(html_body: str) -> str:
        """Convert Q&A pattern lists into block-card grids."""

        def _process_qa_section(match: re.Match[str]) -> str:
            section = match.group(0)
            all_items = re.findall(r"<li>(.*?)</li>", section, re.DOTALL)
            if not all_items:
                return section

            cards = []
            for inner in all_items:
                q_match = re.search(
                    r"(<strong>Q\d+:.*?)(?:<strong>A|A:)", inner, re.DOTALL
                )
                if not q_match:
                    continue

                q_content = q_match.group(1).strip()
                a_start = (
                    q_match.end() - len("<strong>A")
                    if "<strong>A" in inner
                    else q_match.end() - len("A:")
                )
                a_content = inner[a_start:].strip()
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

    @staticmethod
    def _wrap_example_boxes(html_body: str) -> str:
        """Convert ✅/❌ list items under Example headings into styled example-box divs."""

        def _process_examples(match: re.Match[str]) -> str:
            block = match.group(0)
            items = re.findall(r"<li>(✅.*?)</li>|<li>(❌.*?)</li>", block, re.DOTALL)
            if not items:
                return block

            boxes = []
            for good, bad in items:
                if good:
                    klass = "example-box good-box"
                    content = good.strip()
                else:
                    klass = "example-box bad-box"
                    content = bad.strip()
                boxes.append(f'<div class="{klass}"><p>{content}</p></div>')

            remaining = block
            for good, bad in items:
                item = good or bad
                remaining = remaining.replace(f"<li>{item}</li>", "", 1)

            remaining = re.sub(r"<ul>\s*</ul>", "", remaining)

            example_heading = re.search(r"<h4>Example</h4>", remaining)
            if example_heading:
                insert_pos = example_heading.end()
                boxes_html = "\n" + "\n".join(boxes) + "\n"
                remaining = remaining[:insert_pos] + boxes_html + remaining[insert_pos:]

            return remaining

        return re.sub(
            r"<h4>Example</h4>.*?(?=<h[234]>|</section>)",
            _process_examples,
            html_body,
            flags=re.DOTALL,
        )

    @staticmethod
    def _wrap_blockquotes(html_body: str) -> str:
        """Convert <blockquote> elements into styled .blockquotes div cards."""
        return re.sub(
            r"<blockquote>(.*?)</blockquote>",
            r'<div class="blockquotes">\1</div>',
            html_body,
            flags=re.DOTALL,
        )

    @staticmethod
    def _add_blank_target(html_body: str) -> str:
        """Add target="_blank" to all <a> tags that don't already have it."""
        return re.sub(
            r"<a (?![^>]*target=)([^>]*)>",
            r'<a target="_blank" \1>',
            html_body,
        )
