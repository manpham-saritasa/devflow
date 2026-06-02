"""Tests for md-to-html converter."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from frontmatter import extract_metadata, parse_frontmatter
from main import Converter
from md_parser import md_body_to_html, parse_inline
from post_processor import PostProcessor
from pre_processor import PreProcessor

pass_count = 0
fail_count = 0


def check(name: str, actual: Any, expected: Any) -> None:
    global pass_count, fail_count
    if actual == expected:
        pass_count += 1
        print(f"  PASS {name}")
    else:
        fail_count += 1
        print(f"  FAIL {name}")
        print(f"       expected: {expected!r}")
        print(f"       got:      {actual!r}")


def check_true(name: str, condition: bool, actual: Any | None = None) -> None:
    global pass_count, fail_count
    if condition:
        pass_count += 1
        print(f"  PASS {name}")
    else:
        fail_count += 1
        print(f"  FAIL {name}")
        if actual is not None:
            print(f"       got: {actual!r}")


# ── parse_inline ────────────────────────────────────────────────────────────


def test_inline_link_and_code() -> None:
    result = parse_inline("use [docs](https://example.com) and `code`")
    check_true(
        "inline link and code",
        '<a href="https://example.com">docs</a>' in result
        and "<code>code</code>" in result,
        result,
    )


def test_inline_image() -> None:
    result = parse_inline("![alt](img.png)")
    check_true(
        "inline image",
        "<img" in result and 'src="img.png"' in result and "alt" in result,
        result,
    )


# ── md_body_to_html ─────────────────────────────────────────────────────────


def test_blockquote() -> None:
    result = md_body_to_html("> quote")
    check_true(
        "blockquote", "<blockquote>" in result and "<p>quote</p>" in result, result
    )


def test_task_list() -> None:
    result = md_body_to_html("- [x] done\n- [ ] todo")
    check_true(
        "task list",
        'type="checkbox"' in result and "checked" in result and "task-list" in result,
        result,
    )


def test_strikethrough() -> None:
    result = md_body_to_html("~~gone~~")
    check("strikethrough", result, "<p><del>gone</del></p>")


def test_setext_heading() -> None:
    result = md_body_to_html("Title\n=====")
    check("setext heading", result, "<h1>Title</h1>")


def test_reference_link() -> None:
    result = md_body_to_html("[x][id]\n\n[id]: https://example.com")
    check("reference link", result, '<p><a href="https://example.com">x</a></p>')


def test_autolink() -> None:
    result = md_body_to_html("<https://example.com>")
    check(
        "autolink",
        result,
        '<p><a href="https://example.com">https://example.com</a></p>',
    )


def test_mermaid_block() -> None:
    result = md_body_to_html("```mermaid\ngraph TD\n  A-->B\n```")
    check("mermaid block", result, '<pre class="mermaid">\ngraph TD\n  A-->B\n</pre>')


def test_numbered_list_after_paragraph() -> None:
    result = md_body_to_html("Steps:\n1. First\n2. Second")
    check(
        "numbered list after paragraph",
        result,
        "<p>Steps:</p>\n<ol>\n<li>First</li>\n<li>Second</li>\n</ol>",
    )


def test_bullet_list_after_paragraph() -> None:
    result = md_body_to_html("Rules:\n- One\n- Two")
    check(
        "bullet list after paragraph",
        result,
        "<p>Rules:</p>\n<ul>\n<li>One</li>\n<li>Two</li>\n</ul>",
    )


def test_plain_paragraph_preserves_newlines() -> None:
    result = md_body_to_html("Line one.\nLine two.\nLine three.")
    check(
        "plain paragraph preserves newlines",
        result,
        "<p>Line one.<br>\nLine two.<br>\nLine three.</p>",
    )


# ── PostProcessor ───────────────────────────────────────────────────────────


def test_no_h2_content_preserved() -> None:
    result = PostProcessor().process("<p>Intro</p>", "Title", {})
    check_true(
        "no h2 content preserved",
        '<section class="section">\n<p>Intro</p>\n</section>' in result,
        result,
    )


def test_intro_before_h2_preserved() -> None:
    result = PostProcessor().process(
        "<p>Intro</p>\n<h2>Section</h2>\n<p>Body</p>", "Title", {}
    )
    check_true(
        "intro before h2 preserved",
        '<section class="section">\n<p>Intro</p>\n</section>' in result
        and '<section class="section">\n<h2>Section</h2>\n<p>Body</p>\n</section>'
        in result,
        result,
    )


def test_list_line_break_preserved() -> None:
    result = PostProcessor().process(
        "<h2>Section</h2>\n<ul>\n<li>first<br />second</li>\n</ul>", "Title", {}
    )
    check_true("list line break preserved", "<br />" in result, result)


def test_horizontal_rules_removed() -> None:
    result = PostProcessor().process(
        "<h2>Section</h2>\n<p>Body</p>\n<hr />\n<h2>Next</h2>\n<p>More</p>",
        "Title",
        {},
    )
    check_true("horizontal rules removed", "<hr" not in result, result)


def test_table_cell_bullets_become_list() -> None:
    result = PostProcessor().process(
        "<h2>Section</h2>\n<table><thead><tr><th>Col</th></tr></thead><tbody><tr><td>- One<br> - Two<br />* Three</td></tr></tbody></table>",
        "Title",
        {},
    )
    check_true(
        "table cell bullets become list",
        '<td data-label="Col"><ul><li>One</li><li>Two</li><li>Three</li></ul></td>'
        in result,
        result,
    )


def test_h1_has_link() -> None:
    result = PostProcessor._build_header("Hello [world](https://example.com)")
    check_true(
        "h1 renders link", '<a href="https://example.com">world</a>' in result, result
    )


# ── parse_frontmatter / metadata ────────────────────────────────────────────


def test_frontmatter_after_heading() -> None:
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


def test_no_frontmatter() -> None:
    body, fm = parse_frontmatter("# Just a doc\n\nContent.")
    check("no frontmatter - body unchanged", body, "# Just a doc\n\nContent.")
    check("no frontmatter - empty dict", fm, {})


def test_frontmatter_hyphenated_keys() -> None:
    _body, fm = parse_frontmatter(
        "---\nfix-versions: v1.0\ntags:\n  - devops\n  - cloud\n---\n\nBody"
    )
    check("hyphenated key", fm.get("fix-versions"), "v1.0")
    check("unquoted list items", fm.get("tags"), "devops, cloud")


def test_extract_metadata() -> None:
    title, metadata = extract_metadata("# Title\n**Owner:** Jane\n\n---\n\nBody")
    check("metadata title", title, "Title")
    check("metadata value", metadata.get("Owner"), "Jane")


def test_preprocessor_strips_header_metadata_block() -> None:
    source = "# ADR: Sample\n\n**Status:** PROPOSED\n**Task URL:** [X-1](https://example.com)\n**Date:** 2026-05-22\n\n***\n\n## Section\n\nBody"
    body, title, metadata = PreProcessor().process(source, fallback_stem="sample")
    check("preprocessor title", title, "ADR: Sample")
    check("preprocessor metadata status", metadata.get("Status"), "PROPOSED")
    check_true(
        "preprocessor strips header metadata block",
        "**Status:**" not in body
        and "**Task URL:**" not in body
        and "**Date:**" not in body,
        body,
    )
    check_true(
        "preprocessor keeps section body",
        body.startswith("## Section"),
        body,
    )


# ── Converter integration ───────────────────────────────────────────────────


def test_converter_end_to_end() -> None:
    source = "# Demo\n\nIntro text.\n\n## Tasks\n\n- [x] done\n- [ ] todo\n\n> note\n"
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = Path(tmp_dir) / "demo.md"
        html_path = Path(tmp_dir) / "demo.html"
        _ = md_path.write_text(source, encoding="utf-8")
        _ = Converter().convert(md_path, html_path)
        result = html_path.read_text(encoding="utf-8")

    check_true(
        "converter end to end",
        '<section class="header">' in result
        and "Intro text." in result
        and "task-list" in result
        and "blockquotes" in result,
        result,
    )


def test_converter_table_cell_list_fixture() -> None:
    fixture_path = Path(__file__).parent.parent / "test" / "table-cell-lists.md"
    with tempfile.TemporaryDirectory() as tmp_dir:
        html_path = Path(tmp_dir) / "table-cell-lists.html"
        _ = Converter().convert(fixture_path, html_path)
        result = html_path.read_text(encoding="utf-8")

    check_true(
        "converter table cell list fixture",
        '<td data-label="Details"><ul><li>First item</li><li>Second item</li><li>Third item</li></ul></td>'
        in result
        and '<td data-label="Details"><ul><li>Alpha</li><li>Beta</li><li>Gamma</li></ul></td>'
        in result
        and '<td data-label="Details">Single line only</td>' in result,
        result,
    )


# ── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== parse_inline ===")
    test_inline_link_and_code()
    test_inline_image()

    print("\n=== md_body_to_html ===")
    test_blockquote()
    test_task_list()
    test_strikethrough()
    test_setext_heading()
    test_reference_link()
    test_autolink()
    test_mermaid_block()
    test_numbered_list_after_paragraph()
    test_bullet_list_after_paragraph()
    test_plain_paragraph_preserves_newlines()

    print("\n=== PostProcessor ===")
    test_no_h2_content_preserved()
    test_intro_before_h2_preserved()
    test_list_line_break_preserved()
    test_horizontal_rules_removed()
    test_table_cell_bullets_become_list()
    test_h1_has_link()

    print("\n=== parse_frontmatter ===")
    test_frontmatter_after_heading()
    test_no_frontmatter()
    test_frontmatter_hyphenated_keys()
    test_extract_metadata()
    test_preprocessor_strips_header_metadata_block()

    print("\n=== Converter integration ===")
    test_converter_end_to_end()
    test_converter_table_cell_list_fixture()

    print(f"\n{'=' * 40}")
    print(f"Passed: {pass_count}  Failed: {fail_count}")
    print(f"{'=' * 40}")
    sys.exit(0 if fail_count == 0 else 1)
