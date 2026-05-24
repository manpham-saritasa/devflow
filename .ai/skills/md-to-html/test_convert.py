"""Tests for md-to-html converter."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import (
    _build_header,
    _join_split_links,
    extract_metadata,
    parse_frontmatter,
)
from md_parser import md_body_to_html, parse_inline

PASS = 0
FAIL = 0


def check(name, actual, expected):
    global PASS, FAIL
    if actual == expected:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")
        print(f"       expected: {expected!r}")
        print(f"       got:      {actual!r}")


# ── parse_inline ────────────────────────────────────────────────────────────


def test_inline_nested_brackets_link():
    """[[KEY] — [PR title]](url) should produce a link."""
    result = parse_inline("[[KEY] — [PR title]](https://example.com)")
    check(
        "nested brackets link",
        result,
        '<a href="https://example.com">[KEY] — [PR title]</a>',
    )


def test_inline_simple_link():
    """[text](url) should still work."""
    result = parse_inline("[simple](https://example.com)")
    check("simple link", result, '<a href="https://example.com">simple</a>')


def test_inline_code_escapes_html():
    """`<br>` should escape the angle brackets."""
    result = parse_inline("use `<br>` here")
    check("inline code escapes HTML", result, "use <code>&lt;br&gt;</code> here")


# ── md_body_to_html ─────────────────────────────────────────────────────────


def test_heading_with_link():
    """# heading with [link](url) should convert."""
    result = md_body_to_html("# Hello [world](https://example.com)")
    check(
        "heading with link",
        result,
        '<h1>Hello <a href="https://example.com">world</a></h1>',
    )


def test_multi_line_heading():
    """Heading with URL split across lines should join."""
    result = md_body_to_html("# [[KEY] — Title](https\n//github.com/pull/1)")
    check(
        "multi-line heading link",
        result,
        '<h1><a href="https//github.com/pull/1">[KEY] — Title</a></h1>',
    )


def test_multi_line_heading_stops_at_list():
    """Multi-line heading join should stop at list items."""
    result = md_body_to_html("## Source priority\n1. First item\n2. Second item")
    check(
        "heading stops at numbered list",
        result,
        "<h2>Source priority</h2>\n<ol>\n<li>First item</li>\n<li>Second item</li>\n</ol>",
    )


def test_multi_line_heading_stops_at_bullet():
    """Multi-line heading join should stop at bullet list."""
    result = md_body_to_html("## Rules\n- Rule one\n- Rule two")
    check(
        "heading stops at bullet list",
        result,
        "<h2>Rules</h2>\n<ul>\n<li>Rule one</li>\n<li>Rule two</li>\n</ul>",
    )


def test_nested_unordered_list():
    """Indented sub-lists should nest."""
    result = md_body_to_html("- Parent:\n  - Child 1\n  - Child 2\n- Sibling")
    check(
        "nested unordered list",
        result,
        "<ul>\n<li>Parent:<ul><li>Child 1</li><li>Child 2</li></ul></li>\n<li>Sibling</li>\n</ul>",
    )


def test_nested_ordered_list():
    """Indented numbered sub-lists should nest as <ol>."""
    result = md_body_to_html("- Parent:\n  1. First\n  2. Second\n- Sibling")
    check(
        "nested ordered list",
        result,
        "<ul>\n<li>Parent:<ol><li>First</li><li>Second</li></ol></li>\n<li>Sibling</li>\n</ul>",
    )


def test_mermaid_block():
    """```mermaid blocks should render as <pre class=\"mermaid\">."""
    result = md_body_to_html("```mermaid\ngraph TD\n  A-->B\n```")
    check("mermaid block", result, '<pre class="mermaid">\ngraph TD\n  A-->B\n</pre>')


def test_code_block_escaped():
    """Normal code blocks should escape HTML."""
    result = md_body_to_html("```html\n<div>hello</div>\n```")
    check(
        "code block escapes HTML",
        result,
        "<pre><code>&lt;div&gt;hello&lt;/div&gt;</code></pre>",
    )


# ── _join_split_links ───────────────────────────────────────────────────────


def test_join_split_link():
    """Split paragraph link should be joined."""
    result = _join_split_links(
        "<p>[[KEY] — Title](https</p>\n<p>//github.com/pull/1)</p>"
    )
    check(
        "join split paragraph link",
        result,
        "<p>[[KEY] — Title](https//github.com/pull/1)</p>",
    )


def test_join_split_link_no_match():
    """Normal paragraphs should be unchanged."""
    result = _join_split_links("<p>Hello</p>\n<p>World</p>")
    check("no false join", result, "<p>Hello</p>\n<p>World</p>")


# ── _build_header ───────────────────────────────────────────────────────────


def test_eyebrow_split_colon_space():
    """ADR: Title should split on ': '."""
    result = _build_header("ADR: Migrate DB")
    check(
        "eyebrow split on colon-space", "ADR" in result and "Migrate DB" in result, True
    )


def test_no_eyebrow_on_url():
    """Title with https:// should not split eyebrow."""
    result = _build_header("[[KEY] — Title](https://example.com)")
    check("no eyebrow on URL colon", "eyebrow" not in result, True)


def test_h1_has_link():
    """h1 should render markdown links as <a> tags."""
    result = _build_header("Hello [world](https://example.com)")
    check("h1 renders link", '<a href="https://example.com">world</a>' in result, True)


# ── parse_frontmatter ───────────────────────────────────────────────────────


def test_frontmatter_after_heading():
    """Frontmatter after # Heading should be parsed."""
    body, fm = parse_frontmatter(
        "# Skill: test\n\n---\nname: my-skill\ntriggers:\n  - foo\n  - bar\n---\n\n## Section"
    )
    check(
        "frontmatter after heading - body",
        body.strip().startswith("# Skill: test"),
        True,
    )
    check("frontmatter after heading - name", fm.get("name"), "my-skill")
    check("frontmatter after heading - triggers", fm.get("triggers"), "foo, bar")


def test_no_frontmatter():
    """Document without frontmatter should pass through."""
    body, fm = parse_frontmatter("# Just a doc\n\nContent.")
    check("no frontmatter - body unchanged", body, "# Just a doc\n\nContent.")
    check("no frontmatter - empty dict", fm, {})


def test_frontmatter_hyphenated_keys():
    """Keys with hyphens should be parsed."""
    body, fm = parse_frontmatter(
        "---\nfix-versions: v1.0\ntags:\n  - devops\n  - cloud\n---\n\nBody"
    )
    check("hyphenated key", fm.get("fix-versions"), "v1.0")
    check("unquoted list items", fm.get("tags"), "devops, cloud")


# ── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== parse_inline ===")
    test_inline_nested_brackets_link()
    test_inline_simple_link()
    test_inline_code_escapes_html()

    print("\n=== md_body_to_html ===")
    test_heading_with_link()
    test_multi_line_heading()
    test_multi_line_heading_stops_at_list()
    test_multi_line_heading_stops_at_bullet()
    test_nested_unordered_list()
    test_nested_ordered_list()
    test_mermaid_block()
    test_code_block_escaped()

    print("\n=== _join_split_links ===")
    test_join_split_link()
    test_join_split_link_no_match()

    print("\n=== _build_header ===")
    test_eyebrow_split_colon_space()
    test_no_eyebrow_on_url()
    test_h1_has_link()

    print("\n=== parse_frontmatter ===")
    test_frontmatter_after_heading()
    test_no_frontmatter()
    test_frontmatter_hyphenated_keys()

    print(f"\n{'=' * 40}")
    print(f"Passed: {PASS}  Failed: {FAIL}")
    print(f"{'=' * 40}")
    sys.exit(0 if FAIL == 0 else 1)
