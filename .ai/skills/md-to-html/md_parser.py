"""Markdown rendering helpers backed by Python-Markdown."""

from __future__ import annotations

import html
import re
from functools import lru_cache

DEFAULT_EXTENSIONS = [
    "extra",
    "sane_lists",
    "pymdownx.tasklist",
    "pymdownx.tilde",
    "pymdownx.magiclink",
]

DEFAULT_EXTENSION_CONFIGS = {
    "pymdownx.tasklist": {
        "custom_checkbox": False,
        "clickable_checkbox": False,
    },
    "pymdownx.magiclink": {
        "hide_protocol": False,
        "repo_url_shortener": False,
        "repo_url_shorthand": False,
    },
    "pymdownx.tilde": {
        "subscript": False,
    },
}


@lru_cache(maxsize=1)
def _markdown_module():
    try:
        import markdown
    except ImportError as exc:  # pragma: no cover - exercised by runtime, not tests
        raise RuntimeError(
            "Missing Markdown dependencies. Run: python -m pip install -r .ai/skills/md-to-html/requirements.txt (or on Windows: py.exe -m pip install -r .ai/skills/md-to-html/requirements.txt)"
        ) from exc
    return markdown


@lru_cache(maxsize=1)
def _new_renderer():
    markdown = _markdown_module()
    return markdown.Markdown(
        extensions=DEFAULT_EXTENSIONS,
        extension_configs=DEFAULT_EXTENSION_CONFIGS,
        output_format="html",
    )


def _normalize_mermaid_blocks(rendered_html: str) -> str:
    """Convert mermaid fenced code output into the wrapper expected by the page."""

    def _replace(match: re.Match[str]) -> str:
        code = html.unescape(match.group(1)).strip("\n")
        return f'<pre class="mermaid">\n{code}\n</pre>'

    return re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        _replace,
        rendered_html,
        flags=re.DOTALL,
    )


def _is_list_item(stripped: str) -> bool:
    """Check if a line is a bullet or numbered list item."""
    return stripped.startswith(("- ", "* ")) or bool(re.match(r"^\d+\.", stripped))


def _fix_nested_fenced_code(text: str) -> str:
    """Convert fenced code blocks inside list items to indented code blocks.

    Python-Markdown does not render fenced code blocks nested inside list items
    correctly (the content is lost). This converts them to indented (4-space)
    code blocks which Python-Markdown handles properly.
    """
    lines = text.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect indented fenced code block opener (inside list item)
        if stripped.startswith("```") and line != stripped:
            indent = line[: len(line) - len(line.lstrip())]
            info = stripped[3:].strip()  # language specifier, e.g. "bash"

            # Find matching closing fence with same indentation
            j = i + 1
            while j < len(lines):
                if lines[j].strip() == "```" and lines[j].startswith(indent):
                    break
                j += 1

            if j < len(lines):
                code_lines = lines[i + 1 : j]

                # Add blank line before code block (required for indented code in lists)
                result.append("")
                # Python-Markdown sane_lists requires at least 8 spaces for code blocks in lists
                code_indent = "        "
                for cl in code_lines:
                    # Strip existing indent, then add code block indent
                    result.append(code_indent + cl.lstrip())
                # Blank line after code block
                result.append("")

                i = j + 1
                continue

        result.append(line)
        i += 1

    return "\n".join(result)


def _normalize_sublist_indent(text: str) -> str:
    """Normalize 2-space sublist indentation to 4 spaces under colon-ending list items."""
    lines = text.split("\n")
    result: list[str] = []
    in_sublist = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        starts_with_list = _is_list_item(stripped)

        # Detect start of a sublist: list item ending with colon + next line is list item
        if starts_with_list and stripped.endswith(":"):
            # Check if next non-blank line is also a list item
            for j in range(i + 1, len(lines)):
                nxt = lines[j].strip()
                if nxt:
                    if _is_list_item(nxt):
                        in_sublist = True
                    break
            result.append(line)
            continue

        # Handle 2-space indented sublist items
        is_2space = (
            starts_with_list and line.startswith("  ") and not line.startswith("    ")
        )
        if is_2space and in_sublist:
            result.append("    " + stripped)
            continue

        # Exit sublist on non-blank, non-indented, non-list line (or unindented list)
        if stripped and not line.startswith("  "):
            in_sublist = False

        result.append(line)

    return "\n".join(result)


def _insert_blank_before_list(text: str) -> str:
    """Insert blank line between paragraphs and following list items."""
    lines = text.split("\n")
    result: list[str] = []
    for i, line in enumerate(lines):
        result.append(line)
        stripped = line.strip()
        # Not a heading, not a list item, not blank
        if not stripped or stripped.startswith("#") or _is_list_item(stripped):
            continue
        # Check if next non-blank line is a list item
        for j in range(i + 1, len(lines)):
            nxt = lines[j].strip()
            if not nxt:
                continue
            if _is_list_item(nxt):
                result.append("")
            break
    return "\n".join(result)


def _preserve_newlines(text: str) -> str:
    """Add markdown hard-break markers so consecutive lines are not merged into one paragraph."""
    lines = text.split("\n")
    result: list[str] = []
    in_code_block = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Track code block boundaries
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue
        # Never modify content inside code blocks
        if in_code_block:
            result.append(line)
            continue
        # Skip headings, list items, blank lines, table rows, link definitions, indented lines (code blocks)
        if (
            not stripped
            or stripped.startswith("#")
            or stripped.startswith(("- ", "* "))
            or bool(re.match(r"^\d+\.", stripped))
            or stripped.startswith("|")
            or bool(re.match(r"^\[.+\]:", stripped))
            or line.startswith(" ")  # indented code block or list continuation
        ):
            result.append(line)
            continue
        # Look ahead: only add hard break if next non-blank line is also a paragraph line
        has_next = False
        for j in range(i + 1, len(lines)):
            nxt = lines[j].strip()
            if not nxt:
                continue
            if nxt.startswith("```") or bool(re.match(r"^\[.+\]:", nxt)):
                break
            if not (
                nxt.startswith("#")
                or nxt.startswith(("- ", "* "))
                or bool(re.match(r"^\d+\.", nxt))
                or nxt.startswith("|")
            ):
                has_next = True
            break
        if has_next:
            result.append(line.rstrip() + "  ")
        else:
            result.append(line)
    return "\n".join(result)


def md_body_to_html(text: str) -> str:
    """Convert Markdown body text to HTML using a real Markdown parser."""
    text = _fix_nested_fenced_code(text)
    text = _preserve_newlines(text)
    text = _insert_blank_before_list(text)
    text = _normalize_sublist_indent(text)
    renderer = _new_renderer()
    _ = renderer.reset()
    rendered_html = renderer.convert(text)
    return _normalize_mermaid_blocks(rendered_html)


def parse_inline(text: str) -> str:
    """Render an inline Markdown fragment to HTML."""
    rendered = md_body_to_html(text.strip()) if text.strip() else ""
    match = re.fullmatch(r"<p>(.*)</p>", rendered, flags=re.DOTALL)
    return match.group(1) if match else rendered
