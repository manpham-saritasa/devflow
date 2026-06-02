"""Load resources and extract metadata from raw markdown."""

import re
from pathlib import Path

from frontmatter import extract_metadata, parse_frontmatter


class PreProcessor:
    """Load resources and extract metadata from raw markdown."""

    _hr_pattern = re.compile(r"^(\*{3,}|-{3,}|_{3,})\s*$")
    _metadata_line_pattern = re.compile(r"^\*\*(.+?):\*\*\s+(.+)$")

    def __init__(self) -> None:
        here = Path(__file__).parent
        self._css = (here.parent / "assets" / "theme.css").read_text(encoding="utf-8")

    @property
    def css(self) -> str:
        return self._css

    def process(self, md_text: str, fallback_stem: str = "") -> tuple[str, str, dict]:
        """Extract title, metadata, and clean body. Returns (body, title, metadata)."""
        body_text, frontmatter = parse_frontmatter(md_text)
        if frontmatter:
            # YAML frontmatter provides all metadata — skip bold-text extraction
            title, metadata = "", {}
        else:
            # Fallback: extract metadata from **Key:** value patterns (legacy format)
            title, metadata = extract_metadata(body_text)
            body_text = self._strip_header_metadata_block(body_text, title, metadata)
        if not title:
            title = fallback_stem.replace("-", " ").title()
        body_text = self._strip_header_metadata_block(body_text, title, metadata)
        meta = {**metadata, **frontmatter}
        return body_text, title, meta

    def _strip_header_metadata_block(
        self, md_text: str, title: str, metadata: dict[str, str]
    ) -> str:
        """Remove the title-adjacent metadata block after extracting it for header cards."""
        if not title and not metadata:
            return md_text

        lines = md_text.split("\n")
        i = 0

        # Skip leading blank lines
        while i < len(lines) and not lines[i].strip():
            i += 1

        # Preserve blockquote lines that appear before the title heading
        preserved: list[str] = []
        while i < len(lines) and lines[i].strip().startswith(">"):
            preserved.append(lines[i])
            i += 1
        # Also capture blank lines immediately after blockquotes
        while i < len(lines) and not lines[i].strip():
            preserved.append(lines[i])
            i += 1

        # Strip the title heading
        if title and i < len(lines) and lines[i].strip() == f"# {title}":
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1

        # Strip metadata block after title
        consumed_metadata = False
        while i < len(lines):
            stripped = lines[i].strip()
            if not stripped:
                i += 1
                continue
            match = self._metadata_line_pattern.match(stripped)
            if not match or match.group(1).strip() not in metadata:
                break
            consumed_metadata = True
            i += 1

        if consumed_metadata:
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines) and self._hr_pattern.match(lines[i].strip()):
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1

        remaining = "\n".join(lines[i:])
        if preserved:
            remaining = "\n".join(preserved) + "\n" + remaining
        return remaining


# ── PostProcessor ───────────────────────────────────────────────────────────
