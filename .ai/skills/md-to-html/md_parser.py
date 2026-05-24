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
            "Missing Markdown dependencies. Run: python -m pip install -r .ai/skills/md-to-html/requirements.txt"
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


def md_body_to_html(text: str) -> str:
    """Convert Markdown body text to HTML using a real Markdown parser."""
    renderer = _new_renderer()
    _ = renderer.reset()
    rendered_html = renderer.convert(text)
    return _normalize_mermaid_blocks(rendered_html)


def parse_inline(text: str) -> str:
    """Render an inline Markdown fragment to HTML."""
    rendered = md_body_to_html(text.strip()) if text.strip() else ""
    match = re.fullmatch(r"<p>(.*)</p>", rendered, flags=re.DOTALL)
    return match.group(1) if match else rendered
