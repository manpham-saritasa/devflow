"""Tests for jira-move — milestone resolution, pipeline routing, config I/O."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from discover import load_config, save_config
from milestones import Milestones
from pipeline import Pipeline

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_temp_file(name, content):
    path = os.path.join(SKILL_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def rm_temp_file(name):
    path = os.path.join(SKILL_DIR, name)
    if os.path.exists(path):
        os.unlink(path)


# ── Milestones ────────────────────────────────────────────────


def test_milestones_load():
    make_temp_file(
        "milestones.config",
        "PIPELINE=a,b,c\na=Status A,Status A2\nb=Status B\nc=Status C\n",
    )
    ms = Milestones()
    rm_temp_file("milestones.config")
    assert ms.pipeline == ["a", "b", "c"]
    assert ms.milestones["a"] == ["Status A", "Status A2"]


def test_milestones_resolve():
    ms = Milestones()
    ms.milestones = {
        "ready": ["Ready for Development"],
        "review": ["TM Review", "In Review"],
    }
    assert ms.resolve("ready") == "Ready for Development"
    assert ms.resolve("REady") == "Ready for Development"
    assert ms.resolve("TM Review") == "TM Review"


def test_milestones_resolve_picks_existing():
    ms = Milestones()
    ms.milestones = {"pending": ["On Development", "In Progress"]}
    result = ms.resolve("pending", ["Backlog", "In Progress", "Code Review"])
    assert result == "In Progress"


def test_milestones_status_to_ms():
    ms = Milestones()
    ms.milestones = {"ready": ["Ready for Development"], "review": ["TM Review"]}
    assert ms.status_to_milestone("Ready for Development") == "ready"
    assert ms.status_to_milestone("TM Review") == "review"
    assert ms.status_to_milestone("Unknown") is None


def test_milestones_fuzzy():
    ms = Milestones()
    ms.milestones = {"complete": ["Completed"]}
    assert ms.status_to_milestone("Completed.") == "complete"


def test_milestones_next():
    ms = Milestones()
    ms.milestones = {"a": ["A"], "b": ["B"], "c": ["C"]}
    ms.pipeline = ["a", "b", "c"]
    assert ms.next("a") == "b"
    assert ms.next("c") is None
    assert ms.next("x") is None


def test_milestones_is_last():
    ms = Milestones()
    ms.pipeline = ["a", "b", "c"]
    assert not ms.is_last("a")
    assert ms.is_last("c")


# ── Pipeline ──────────────────────────────────────────────────


def test_pipeline_path_to():
    ms = Milestones()
    ms.pipeline = ["backlog", "ready", "pending", "review"]
    pl = Pipeline(ms)
    assert pl.path_to("backlog", "review") == ["ready", "pending", "review"]
    assert pl.path_to("review", "backlog") == []
    assert pl.path_to("ready", "pending") == ["pending"]


def test_pipeline_is_ahead():
    ms = Milestones()
    ms.pipeline = ["a", "b", "c"]
    pl = Pipeline(ms)
    assert pl.is_ahead("a", "c")
    assert not pl.is_ahead("c", "a")


# ── Config I/O ────────────────────────────────────────────────


def test_load_config_transition_map():
    make_temp_file(
        "test.config",
        "Backlog=10=Blocked,221=Ready for Development\n"
        "In Progress=311=Code Review,351=Ready for Development\n",
    )
    config = load_config("test")
    rm_temp_file("test.config")
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
    assert config["transitions"]["Backlog"] == {"10": "Blocked"}


def test_load_config_with_milestones():
    make_temp_file(
        "test.config",
        "ready=Ready for Development\nreview=TM Review\n\nBacklog=10=Blocked\n",
    )
    config = load_config("test")
    rm_temp_file("test.config")
    assert config["milestones"] == {
        "ready": ["Ready for Development"],
        "review": ["TM Review"],
    }
    assert config["transitions"]["Backlog"] == {"10": "Blocked"}


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
    assert loaded["milestones"] == {
        "ready": ["Ready for Development"],
        "review": ["TM Review"],
    }
    assert loaded["transitions"]["Backlog"] == {
        "10": "Blocked",
        "221": "Ready for Development",
    }


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
