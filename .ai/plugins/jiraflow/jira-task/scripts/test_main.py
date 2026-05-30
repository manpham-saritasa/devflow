"""Tests for jira-task main.py — pure functions only (no network)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import build_output, group_tasks


def make_issue(key, status, priority, summary="Test task", description=None):
    fields = {
        "summary": summary,
        "status": {"name": status},
        "priority": {"name": priority},
        "issuetype": {"name": "Task"},
        "updated": "2026-01-01T00:00:00.000+0000",
    }
    if description:
        fields["description"] = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description}],
                }
            ],
        }
    return {"key": key, "fields": fields}


def test_group_ongoing():
    issues = [make_issue("T-1", "In Progress", "High")]
    ongoing, ready = group_tasks(issues, set())
    assert len(ongoing) == 1
    assert len(ready) == 0
    assert ongoing[0]["key"] == "T-1"


def test_group_ready():
    issues = [make_issue("T-1", "Open", "Medium")]
    ongoing, ready = group_tasks(issues, set())
    assert len(ongoing) == 0
    assert len(ready) == 1
    assert ready[0]["key"] == "T-1"


def test_group_mixed():
    issues = [
        make_issue("T-1", "In Progress", "High"),
        make_issue("T-2", "Open", "Low"),
        make_issue("T-3", "Code Review", "Medium"),
    ]
    ongoing, ready = group_tasks(issues, set())
    assert len(ongoing) == 2
    assert len(ready) == 1
    assert ready[0]["key"] == "T-2"


def test_group_unknown_status():
    issues = [make_issue("T-1", "Some Weird Status", "High")]
    ongoing, ready = group_tasks(issues, set())
    assert len(ongoing) == 1
    assert len(ready) == 0


def test_group_ignored():
    issues = [
        make_issue("T-1", "In Progress", "High"),
        make_issue("T-2", "Open", "Low"),
    ]
    ongoing, ready = group_tasks(issues, {"T-1"})
    assert len(ongoing) == 0
    assert len(ready) == 1
    assert ready[0]["key"] == "T-2"


def test_sort_ongoing_by_priority():
    issues = [
        make_issue("T-1", "In Progress", "Low"),
        make_issue("T-2", "In Progress", "Highest"),
        make_issue("T-3", "In Progress", "Medium"),
    ]
    ongoing, _ = group_tasks(issues, set())
    assert ongoing[0]["key"] == "T-2"
    assert ongoing[1]["key"] == "T-3"
    assert ongoing[2]["key"] == "T-1"


def test_sort_ready_by_priority():
    issues = [
        make_issue("T-1", "Open", "Low"),
        make_issue("T-2", "To Do", "Highest"),
        make_issue("T-3", "Ready for Development", "Medium"),
    ]
    _, ready = group_tasks(issues, set())
    assert ready[0]["key"] == "T-2"
    assert ready[1]["key"] == "T-3"
    assert ready[2]["key"] == "T-1"


def test_build_output_empty():
    output = build_output([], [], 0, "TEST", "2026-01-01")
    assert "No pending tasks" in output


def test_build_output_ongoing_only():
    ongoing = [
        {
            "key": "T-1",
            "url": "https://example.com/T-1",
            "priority": "High",
            "status": "In Progress",
            "summary": "Fix bug",
        },
    ]
    output = build_output(ongoing, [], 0, "TEST", "2026-01-01")
    assert "### 1. [T-1]" in output
    assert "**Fix bug:**" in output
    assert "On-Going" in output
    assert "Ready for Development" not in output


def test_build_output_ready_only():
    ready = [
        {
            "key": "T-2",
            "url": "https://example.com/T-2",
            "priority": "Medium",
            "status": "Open",
            "summary": "Add feature",
        },
    ]
    output = build_output([], ready, 0, "TEST", "2026-01-01")
    assert "T-2" in output
    assert "Ready for Development" in output
    assert "On-Going" not in output


def test_build_output_both_groups():
    ongoing = [
        {
            "key": "T-1",
            "url": "https://example.com/T-1",
            "priority": "High",
            "status": "In Progress",
            "summary": "Fix bug",
        },
    ]
    ready = [
        {
            "key": "T-2",
            "url": "https://example.com/T-2",
            "priority": "Low",
            "status": "Open",
            "summary": "Add feature",
        },
    ]
    output = build_output(ongoing, ready, 3, "TEST", "2026-01-01")
    assert "2 pending" in output
    assert "3 ignored" in output
    assert "On-Going (1)" in output
    assert "Ready for Development (1)" in output


def test_build_output_includes_url():
    ongoing = [
        {
            "key": "T-1",
            "url": "https://example.com/T-1",
            "priority": "High",
            "status": "In Progress",
            "summary": "Fix bug",
        },
    ]
    output = build_output(ongoing, [], 0, "TEST", "2026-01-01")
    assert "https://example.com/T-1" in output


def test_build_output_includes_description():
    ongoing = [
        {
            "key": "T-1",
            "url": "https://example.com/T-1",
            "priority": "High",
            "status": "In Progress",
            "summary": "Fix bug",
            "description": "The login page crashes when user enters invalid email.",
        },
    ]
    output = build_output(ongoing, [], 0, "TEST", "2026-01-01")
    assert "The login page crashes" in output


def test_group_includes_description():
    issues = [
        make_issue(
            "T-1", "In Progress", "High", "Fix bug", "Login crashes on invalid email"
        )
    ]
    ongoing, _ = group_tasks(issues, set())
    assert "Login crashes on invalid email" in ongoing[0]["description"]


def test_extract_text_spacing():
    from main import extract_text

    node = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "First sentence."}],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Second sentence."}],
            },
        ],
    }
    result = extract_text(node)
    assert "First sentence. Second sentence." in result


def test_group_no_description():
    issues = [make_issue("T-1", "In Progress", "High", "Fix bug")]
    ongoing, _ = group_tasks(issues, set())
    assert ongoing[0]["description"] == ""


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
