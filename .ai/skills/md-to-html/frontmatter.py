"""YAML frontmatter and metadata extraction for markdown documents."""

import re


def parse_frontmatter(md_text: str):
    """Parse YAML-like frontmatter between --- delimiters at the top of a document.

    Returns (body_without_frontmatter, frontmatter_dict).
    Keys with list values are joined with ', ' for display.
    """
    lines = md_text.split("\n")
    if not lines:
        return md_text, {}

    # Find opening --- on line 0 only (frontmatter must be at top of file)
    if not lines or lines[0].strip() != "---":
        return md_text, {}
    start = 0

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
    """Extract title and metadata key-value pairs from the first lines of the body.

    Only scans the first 12 lines, stopping early at the first HR (*** or ---).
    """
    lines = md_text.split("\n")
    title = ""
    metadata = {}

    for i, line in enumerate(lines):
        if i >= 12:
            break
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
