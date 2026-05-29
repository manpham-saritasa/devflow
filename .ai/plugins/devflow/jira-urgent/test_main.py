"""Tests for jira-urgent main.py — pure functions only (no network)."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import (
    build_output,
    classify_intent,
    extract_text,
    find_urgent_comment,
    has_mention,
    sort_urgent,
)

# ── extract_text ──────────────────────────────────────────────


def test_extract_text_plain_string():
    assert extract_text("hello") == "hello"


def test_extract_text_atdoc_text_node():
    node = {"type": "text", "text": "hello world"}
    assert extract_text(node) == "hello world"


def test_extract_text_atdoc_mention():
    node = {"type": "mention", "attrs": {"id": "abc", "text": "Quan Dao"}}
    assert extract_text(node) == "@Quan Dao"


def test_extract_text_atdoc_hard_break():
    node = {"type": "hardBreak"}
    assert extract_text(node) == "\n"


def test_extract_text_atdoc_paragraph():
    node = {
        "type": "paragraph",
        "content": [
            {"type": "text", "text": "Hello "},
            {"type": "mention", "attrs": {"id": "123", "text": "Quan Dao"}},
            {"type": "text", "text": " please verify."},
        ],
    }
    assert extract_text(node) == "Hello @Quan Dao please verify."


def test_extract_text_nested_doc():
    node = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Line 1"},
                    {"type": "hardBreak"},
                    {"type": "text", "text": "Line 2"},
                ],
            }
        ],
    }
    assert extract_text(node) == "Line 1\nLine 2"


def test_extract_text_list():
    nodes = [
        {"type": "text", "text": "A"},
        {"type": "text", "text": "B"},
    ]
    assert extract_text(nodes) == "AB"


# ── has_mention ────────────────────────────────────────────────


def test_has_mention_found():
    node = {
        "type": "paragraph",
        "content": [
            {"type": "mention", "attrs": {"id": "user-123", "text": "Quan Dao"}},
            {"type": "text", "text": " check this."},
        ],
    }
    assert has_mention(node, "user-123") is True


def test_has_mention_not_found():
    node = {
        "type": "paragraph",
        "content": [
            {"type": "mention", "attrs": {"id": "user-456", "text": "Other"}},
            {"type": "text", "text": " hello."},
        ],
    }
    assert has_mention(node, "user-123") is False


def test_has_mention_no_mentions():
    node = {"type": "paragraph", "content": [{"type": "text", "text": "plain text"}]}
    assert has_mention(node, "user-123") is False


def test_has_mention_string():
    assert has_mention("plain string", "user-123") is False


def test_has_mention_nested_mention():
    node = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "asked "},
                    {
                        "type": "mention",
                        "attrs": {"id": "user-123", "text": "Quan Dao"},
                    },
                ],
            }
        ],
    }
    assert has_mention(node, "user-123") is True


# ── classify_intent ───────────────────────────────────────────


def test_classify_verify_fixed():
    assert classify_intent("The bug is fixed on dev.") == "verify"


def test_classify_verify_resolved():
    assert classify_intent("This issue is resolved now.") == "verify"


def test_classify_verify_please_check():
    assert classify_intent("Please check when you have time.") == "verify"


def test_classify_verify_please_verify():
    assert classify_intent("Could you please verify?") == "verify"


def test_classify_verify_ready_for_review():
    assert classify_intent("Ready for review on staging.") == "verify"


def test_classify_verify_worked_on_dev():
    assert classify_intent("Worked on dev, passing now.") == "verify"


def test_classify_at_mention_default():
    assert classify_intent("Here is the mock UI with data.") == "at_mention"


def test_classify_at_mention_question():
    assert classify_intent("What should we do about this?") == "at_mention"


def test_classify_case_insensitive():
    assert classify_intent("RESOLVED on production.") == "verify"


# ── find_urgent_comment ───────────────────────────────────────

ACCOUNT_ID = "user-me"


def make_comment(author_id, body_text, comment_id="1"):
    return {
        "id": comment_id,
        "author": {"accountId": author_id, "displayName": author_id},
        "body": {
            "type": "doc",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": body_text}]}
            ],
        },
    }


def make_mention_comment(author_id, mention_id, comment_id="1"):
    return {
        "id": comment_id,
        "author": {"accountId": author_id, "displayName": author_id},
        "body": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "mention",
                            "attrs": {"id": mention_id, "text": "Someone"},
                        },
                        {"type": "text", "text": " please check."},
                    ],
                }
            ],
        },
    }


def test_find_urgent_mention():
    comments = [make_mention_comment("other", ACCOUNT_ID)]
    result = find_urgent_comment(comments, ACCOUNT_ID, set())
    assert result is not None
    assert result["author"] == "other"


def test_find_urgent_question():
    comments = [make_comment("other", "What do you think?")]
    result = find_urgent_comment(comments, ACCOUNT_ID, set())
    assert result is not None


def test_find_urgent_skips_own_comment():
    comments = [
        make_comment("other", "What do you think?"),
        make_comment(ACCOUNT_ID, "I replied."),
    ]
    result = find_urgent_comment(comments, ACCOUNT_ID, set())
    assert result is None


def test_find_urgent_skips_ignored():
    comments = [make_mention_comment("other", ACCOUNT_ID, comment_id="999")]
    result = find_urgent_comment(comments, ACCOUNT_ID, {"999"})
    assert result is None


def test_find_urgent_no_match():
    comments = [make_comment("other", "Looks good.")]
    result = find_urgent_comment(comments, ACCOUNT_ID, set())
    assert result is None


def test_find_urgent_empty_comments():
    result = find_urgent_comment([], ACCOUNT_ID, set())
    assert result is None


def test_find_urgent_latest_urgent_wins():
    comments = [
        make_comment("other", "Old question?"),
        make_comment("other2", "New question?"),
    ]
    result = find_urgent_comment(comments, ACCOUNT_ID, set())
    assert result is not None
    assert result["author"] == "other2"


# ── sort_urgent ───────────────────────────────────────────────


def test_sort_blocked_first():
    items = [
        {"status": "In Progress", "tag": "at_mention", "priority": "High"},
        {"status": "Blocked", "tag": "at_mention", "priority": "Medium"},
    ]
    sort_urgent(items)
    assert items[0]["status"] == "Blocked"


def test_sort_at_mention_before_verify():
    items = [
        {"status": "In Progress", "tag": "verify", "priority": "High"},
        {"status": "In Progress", "tag": "at_mention", "priority": "High"},
    ]
    sort_urgent(items)
    assert items[0]["tag"] == "at_mention"


def test_sort_priority_descending():
    items = [
        {"status": "In Progress", "tag": "at_mention", "priority": "Low"},
        {"status": "In Progress", "tag": "at_mention", "priority": "Highest"},
    ]
    sort_urgent(items)
    assert items[0]["priority"] == "Highest"


def test_sort_unknown_status_last():
    items = [
        {"status": "Unknown", "tag": "at_mention", "priority": "Highest"},
        {"status": "In Progress", "tag": "at_mention", "priority": "Low"},
    ]
    sort_urgent(items)
    assert items[0]["status"] == "In Progress"


# ── build_output ──────────────────────────────────────────────


def test_build_output_empty():
    output = build_output([], 0, "TEST", "example", "2026-01-01")
    assert "No urgent items" in output
    assert "**0 urgent**" in output


def test_build_output_single():
    items = [
        {
            "key": "TEST-1",
            "comment_id": "123",
            "status": "In Progress",
            "priority": "High",
            "author": "Alice",
            "tag": "at_mention",
        }
    ]
    output = build_output(items, 0, "TEST", "example", "2026-01-01")
    assert "**1 urgent**" in output
    assert "TEST-1" in output
    assert "focusedCommentId=123" in output
    assert "at_mention" in output


def test_build_output_multiple():
    items = [
        {
            "key": "TEST-1",
            "comment_id": "1",
            "status": "In Progress",
            "priority": "High",
            "author": "A",
            "tag": "at_mention",
        },
        {
            "key": "TEST-2",
            "comment_id": "2",
            "status": "TM Review",
            "priority": "Medium",
            "author": "B",
            "tag": "verify",
        },
    ]
    output = build_output(items, 3, "TEST", "example", "2026-01-01")
    assert "**2 urgent**" in output
    assert "(3 ignored)" in output
    assert "TEST-1" in output
    assert "TEST-2" in output


if __name__ == "__main__":
    passed = 0
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
                print(f"  PASS {name}")
            except Exception as e:
                failed += 1
                print(f"  FAIL {name}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
