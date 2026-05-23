"""Markdown to flat HTML body converter."""

import html
import re
from dataclasses import dataclass, field


def parse_inline(t: str) -> str:
    """Convert inline Markdown formatting to HTML."""
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    return t


@dataclass
class _State:
    """Mutable parser state shared across line handlers."""

    in_table: bool = False
    table_header_done: bool = False
    in_list: bool = False
    list_tag: str = "ul"
    in_code_block: bool = False
    code_buf: list = field(default_factory=list)


def md_body_to_html(text: str) -> str:
    """Convert Markdown body text to flat HTML (no page wrapper)."""
    lines = text.split("\n")
    out = []
    state = _State()
    emit = out.append
    i = 0
    while i < len(lines):
        i = _process_line(lines, i, state, emit)
    if state.in_list:
        emit(f"</{state.list_tag}>")
    if state.in_table:
        emit("</tbody></table>")
    return "\n".join(out)


def _process_line(lines, i, state, emit):
    """Dispatch a single markdown line. Returns next index."""
    line = lines[i]

    if line.strip().startswith("```"):
        return _handle_code_block(line, state, emit, i)
    if state.in_code_block:
        state.code_buf.append(line + "\n")
        return i + 1

    if line.strip() == "":
        if state.in_list:
            emit(f"</{state.list_tag}>")
            state.in_list = False
        return i + 1

    if re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", line.strip()):
        _close_table(state, emit)
        return i + 1

    m = re.match(r"^(#{1,6})\s+(.+)$", line)
    if m:
        _close_table(state, emit)
        if state.in_list:
            emit(f"</{state.list_tag}>")
            state.in_list = False
        level = min(len(m.group(1)), 3)
        emit(f"<h{level}>{parse_inline(m.group(2))}</h{level}>")
        return i + 1

    if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
        if state.in_table:
            state.table_header_done = True
        return i + 1
    if line.strip().startswith("|") and line.strip().endswith("|"):
        _emit_table_row(line, state, emit)
        return i + 1
    _close_table(state, emit)

    m_ul = re.match(r"^(\s*)[-*]\s+(.+)$", line)
    if m_ul:
        return _handle_list(lines, i, "ul", m_ul.group(2), state, emit)
    m_ol = re.match(r"^(\s*)\d+\.\s+(.+)$", line)
    if m_ol:
        return _handle_list(lines, i, "ol", m_ol.group(2), state, emit)

    content = parse_inline(line.strip())
    if content:
        emit(f"<p>{content}</p>")
    return i + 1

# ── Line handlers ───────────────────────────────────────────────────────────


def _handle_code_block(line: str, state: _State, emit, i: int) -> int:
    """Open or close a fenced code block. Returns next line index."""
    if state.in_code_block:
        escaped = html.escape("".join(state.code_buf).rstrip())
        emit(f"<pre><code>{escaped}</code></pre>")
        state.code_buf = []
        state.in_code_block = False
    else:
        state.in_code_block = True
    return i + 1


def _close_table(state: _State, emit) -> None:
    if state.in_table:
        emit("</tbody></table>")
        state.in_table = False
        state.table_header_done = False


def _emit_table_row(line: str, state: _State, emit) -> None:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if not state.in_table:
        state.in_table = True
        state.table_header_done = False
        emit("<table><thead>")
    if not state.table_header_done:
        emit("<tr>" + "".join(f"<th>{parse_inline(c)}</th>" for c in cells) + "</tr>")
        emit("</thead><tbody>")
        state.table_header_done = True
    else:
        emit("<tr>")
        for c in cells:
            c_html = parse_inline(c)
            if "<br>" in c_html or re.search(r"(?:^|\s)-\s", c):
                c_html = _cell_to_list(c_html)
            emit(f"<td>{c_html}</td>")
        emit("</tr>")


def _handle_list(
    lines: list[str], i: int, tag: str, content: str, state: _State, emit
) -> int:
    """Handle a list item, including multi-line continuations. Returns next index."""
    if not state.in_list or state.list_tag != tag:
        if state.in_list:
            emit(f"</{state.list_tag}>")
        state.in_list = True
        state.list_tag = tag
        emit(f"<{tag}>")

    html_content = parse_inline(content)
    j = i + 1
    while j < len(lines) and lines[j].strip():
        next_line = lines[j].strip()
        if (
            re.match(r"^(\s*)[-*]\s+", lines[j])
            or re.match(r"^\s*\d+\.\s+", lines[j])
            or next_line.startswith("#")
            or next_line.startswith("|")
            or next_line.startswith("```")
            or re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", next_line)
        ):
            break
        html_content += "<br>" + parse_inline(next_line)
        j += 1

    emit(f"<li>{html_content}</li>")
    return j


def _cell_to_list(cell_html: str) -> str:
    """Convert <br>-separated bullet items in a table cell to <ul><li>."""
    parts = [p.strip() for p in cell_html.split("<br>") if p.strip()]
    if len(parts) <= 1:
        return cell_html
    bullet_count = sum(1 for p in parts if re.match(r"^[-*]\s", p))
    if bullet_count >= len(parts) * 0.5:
        items = [re.sub(r"^[-*]\s+", "", p) for p in parts]
        return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"
    return cell_html
