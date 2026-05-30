"""Tests for jira-move main.py — pure functions only (no network)."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import (
    load_config,
    load_milestones,
    resolve_target,
    save_config,
    status_to_milestone,
)

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))


def make_temp_file(name, content):
    path = os.path.join(SKILL_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def rm_temp_file(name):
    path = os.path.join(SKILL_DIR, name)
    if os.path.exists(path):
        os.unlink(path)


# ── load_milestones ───────────────────────────────────────────


def test_load_milestones_basic():
    make_temp_file(
        "milestones.config",
        "PIPELINE=a,b,c\na=Status A,Status A2\nb=Status B\nc=Status C\n",
    )
    milestones, pipeline = load_milestones()
    rm_temp_file("milestones.config")
    assert pipeline == ["a", "b", "c"]
    assert milestones["a"] == ["Status A", "Status A2"]
    assert milestones["b"] == ["Status B"]
    assert milestones["c"] == ["Status C"]


# ── status_to_milestone ───────────────────────────────────────


def test_status_to_milestone_exact():
    milestones = {
        "ready": ["Ready for Development"],
        "review": ["TM Review", "In Review"],
    }
    assert status_to_milestone("Ready for Development", milestones) == "ready"
    assert status_to_milestone("ready for development", milestones) == "ready"
    assert status_to_milestone("TM Review", milestones) == "review"
    assert status_to_milestone("In Review", milestones) == "review"


def test_status_to_milestone_substring():
    milestones = {"pending": ["In Progress"], "verify": ["On Staging"]}
    assert status_to_milestone("in progress", milestones) == "pending"
    assert status_to_milestone("on staging", milestones) == "verify"


def test_status_to_milestone_not_found():
    milestones = {"ready": ["Ready for Development"]}
    assert status_to_milestone("Some Unknown Status", milestones) is None


def test_status_to_milestone_fuzzy_match():
    milestones = {"complete": ["Completed"]}
    assert status_to_milestone("Completed.", milestones) == "complete"


# ── resolve_target ────────────────────────────────────────────


def test_resolve_target_milestone_name():
    milestones = {
        "ready": ["Ready for Development", "Ready to Do"],
        "review": ["TM Review"],
    }
    assert resolve_target("ready", milestones) == "Ready for Development"
    assert resolve_target("REady", milestones) == "Ready for Development"


def test_resolve_target_status_name():
    milestones = {"review": ["TM Review", "In Review"]}
    assert resolve_target("TM Review", milestones) == "TM Review"
    assert resolve_target("tm review", milestones) == "TM Review"


def test_resolve_target_unknown():
    milestones = {"ready": ["Ready for Development"]}
    assert resolve_target("unknown", milestones) == "unknown"


def test_resolve_target_multiple_statuses():
    milestones = {"ready": ["Ready for Development", "Ready to Do"]}
    assert resolve_target("Ready to Do", milestones) == "Ready to Do"


def test_resolve_target_prefers_project():
    global_ms = {"ready": ["Ready for Development"]}
    project_ms = {"ready": ["Ready to Do"]}
    assert resolve_target("ready", global_ms, project_ms) == "Ready to Do"


def test_resolve_target_falls_back_to_global():
    global_ms = {"ready": ["Ready for Development"]}
    project_ms = {}
    assert resolve_target("ready", global_ms, project_ms) == "Ready for Development"


# ── load_config / save_config ─────────────────────────────────


def test_load_config_transition_map():
    make_temp_file(
        "test.config",
        "# Comment\n"
        "Backlog=10=Blocked,221=Ready for Development\n"
        "In Progress=311=Code Review,351=Ready for Development\n",
    )
    config = load_config("test")
    rm_temp_file("test.config")
    assert config is not None
    assert config["transitions"]["Backlog"] == {
        "10": "Blocked",
        "221": "Ready for Development",
    }
    assert config["transitions"]["In Progress"] == {
        "311": "Code Review",
        "351": "Ready for Development",
    }


def test_load_config_ignores_pipeline():
    make_temp_file("test.config", "PIPELINE=Backlog, Ready\nBacklog=10=Blocked\n")
    config = load_config("test")
    rm_temp_file("test.config")
    assert config is not None
    assert config["transitions"]["Backlog"] == {"10": "Blocked"}


def test_load_config_missing():
    config = load_config("nonexistent")
    assert config is None


def test_save_config_roundtrip():
    config = {
        "milestones": {"ready": ["Ready for Development"], "review": ["TM Review"]},
        "transitions": {
            "Backlog": {"10": "Blocked", "221": "Ready for Development"},
            "Ready for Development": {"231": "In Progress", "241": "Backlog"},
        },
    }
    save_config("test", config)
    loaded = load_config("test")
    rm_temp_file("test.config")
    assert loaded is not None
    assert loaded["milestones"] == {
        "ready": ["Ready for Development"],
        "review": ["TM Review"],
    }
    assert loaded["transitions"]["Backlog"] == {
        "10": "Blocked",
        "221": "Ready for Development",
    }
    assert loaded["transitions"]["Ready for Development"] == {
        "231": "In Progress",
        "241": "Backlog",
    }


# ── Pipeline routing ─────────────────────────────────────────


def test_resolve_target_picks_existing_status():
    """When project doesn't have 'On Development' but has 'In Progress', pick 'In Progress'"""
    global_ms = {"pending": ["On Development", "Doing", "In Progress"]}
    project_keys = ["Backlog", "Ready for Development", "In Progress", "Code Review"]
    result = resolve_target("pending", global_ms, None, project_keys)
    assert result == "In Progress"


def test_pipeline_routing_order():
    """From 'backlog', routing to 'review' should go through 6 milestones"""
    pipeline = [
        "backlog",
        "ready",
        "pending",
        "code-review",
        "ready-for-qa",
        "in-qa",
        "review",
        "verify",
        "complete",
    ]
    current_idx = pipeline.index("backlog")
    target_idx = pipeline.index("review")
    steps = pipeline[current_idx + 1 : target_idx + 1]
    assert steps == [
        "ready",
        "pending",
        "code-review",
        "ready-for-qa",
        "in-qa",
        "review",
    ]
    assert len(steps) == 6


if __name__ == "__main__":
    passed = 0
    failed = 0
    total = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            total += 1
            try:
                fn()
                passed += 1
                print(f"  PASS {name}")
            except Exception as e:
                failed += 1
                print(f"  FAIL {name}: {e}")
    print(f"\n{passed}/{total} passed, {failed} failed")
    if failed:
        sys.exit(1)
