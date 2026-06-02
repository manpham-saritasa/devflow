"""
md-to-html — Convert Markdown files into polished standalone HTML files.

Usage:
    python main.py <input.md> [output.html]
"""

import sys
from pathlib import Path

from md_parser import md_body_to_html
from post_processor import PostProcessor
from pre_processor import PreProcessor


class Converter:
    """Orchestrate markdown-to-HTML conversion."""

    def __init__(self) -> None:
        self._pre = PreProcessor()
        self._post = PostProcessor()

    @property
    def css(self) -> str:
        return self._pre.css

    def convert(self, md_path: Path, out_path: Path) -> Path:
        """Convert a Markdown file to HTML and write to out_path."""
        md_text = md_path.read_text(encoding="utf-8")
        body_text, title, meta = self._pre.process(md_text, fallback_stem=md_path.stem)

        body_html = md_body_to_html(body_text)
        final_body = self._post.process(body_html, title, meta)

        mermaid_script = ""
        if 'class="mermaid"' in final_body:
            mermaid_script = (
                '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js">'
                "</script>\n"
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
{self.css}
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


# ── CLI ─────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input.md> [output.html]")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"Error: file not found: {md_path}")
        sys.exit(1)

    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else md_path.with_suffix(".html")
    result = Converter().convert(md_path, out_path)
    print(f"HTML written to {result} ({result.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
