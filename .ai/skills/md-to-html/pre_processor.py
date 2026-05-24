"""Load resources and extract metadata from raw markdown."""
from pathlib import Path
from frontmatter import parse_frontmatter, extract_metadata

class PreProcessor:
    """Load resources and extract metadata from raw markdown."""

    def __init__(self) -> None:
        here = Path(__file__).parent
        self._css = (here / "theme.css").read_text(encoding="utf-8")

    @property
    def css(self) -> str:
        return self._css

    def process(self, md_text: str, fallback_stem: str = "") -> tuple[str, str, dict]:
        """Extract title, metadata, and clean body. Returns (body, title, metadata)."""
        body_text, frontmatter = parse_frontmatter(md_text)
        title, metadata = extract_metadata(body_text)
        if not title:
            title = fallback_stem.replace("-", " ").title()
        meta = {**metadata, **frontmatter}
        return body_text, title, meta


# ── PostProcessor ───────────────────────────────────────────────────────────


