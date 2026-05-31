"""Structural tests for devflow plugin — validates SKILL.md files, paths, and cross-references."""

import os
import sys

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def exists(path):
    return os.path.exists(path)


def skills():
    """Return list of skill directories with SKILL.md."""
    result = []
    for entry in sorted(os.listdir(PLUGIN_DIR)):
        d = os.path.join(PLUGIN_DIR, entry)
        if os.path.isdir(d) and exists(os.path.join(d, "SKILL.md")):
            result.append(entry)
    return result


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip(chr(34)).strip(""").strip(""")
    return fm


def parse_triggers(text):
    if not text.startswith("---"):
        return []
    end = text.find("---", 3)
    if end == -1:
        return []
    fm = text[3:end]
    items = []
    in_list = False
    for line in fm.split("\n"):
        s = line.strip()
        if s.startswith("triggers:"):
            in_list = True
            continue
        if in_list:
            if s.startswith("- "):
                items.append(s[2:].strip().strip('"'))
            elif s and not s.startswith("-"):
                break
    return items


# ── Config ────────────────────────────────────────────────────


def test_config_exists():
    assert exists(os.path.join(PLUGIN_DIR, "config.md"))


def test_config_has_required_vars():
    c = read(os.path.join(PLUGIN_DIR, "config.md"))
    for var in ["TASKS_ROOT", "TASK_DIR", "ADR_DIR", "MERGE_STRATEGY"]:
        assert var in c, f"config.md missing {var}"


def test_config_template_vars():
    c = read(os.path.join(PLUGIN_DIR, "config.md"))
    for var in [
        "PLAN_TEMPLATE",
        "PROGRESS_TEMPLATE",
        "CHANGELOG_TEMPLATE",
        "REVIEW_TEMPLATE",
    ]:
        assert var in c, f"config.md missing {var}"


# ── Agent ─────────────────────────────────────────────────────


def test_agent_exists():
    assert exists(os.path.join(PLUGIN_DIR, "agent.md"))


def test_agent_has_frontmatter():
    fm = parse_frontmatter(read(os.path.join(PLUGIN_DIR, "agent.md")))
    assert fm.get("name") == "devflow"


def test_agent_references_config():
    c = read(os.path.join(PLUGIN_DIR, "agent.md"))
    assert "config.md" in c, "agent.md missing config.md reference"


def test_agent_has_detection_table():
    c = read(os.path.join(PLUGIN_DIR, "agent.md"))
    assert "Detect Current Progress" in c


# ── Skills ────────────────────────────────────────────────────


def test_all_skills_have_frontmatter():
    for s in skills():
        fm = parse_frontmatter(read(os.path.join(PLUGIN_DIR, s, "SKILL.md")))
        assert fm, f"{s}/SKILL.md has no frontmatter"
        assert "name" in fm, f"{s}/SKILL.md missing name"
        assert "description" in fm, f"{s}/SKILL.md missing description"


def test_all_skills_have_triggers():
    for s in skills():
        triggers = parse_triggers(read(os.path.join(PLUGIN_DIR, s, "SKILL.md")))
        assert len(triggers) > 0, f"{s}/SKILL.md has no triggers"


def test_all_skills_have_workflow():
    for s in skills():
        c = read(os.path.join(PLUGIN_DIR, s, "SKILL.md"))
        assert "## Workflow" in c, f"{s}/SKILL.md missing ## Workflow"


def test_all_skills_reference_config():
    for s in skills():
        c = read(os.path.join(PLUGIN_DIR, s, "SKILL.md"))
        assert "config.md" in c, f"{s}/SKILL.md missing config.md reference"


def test_skill_count():
    assert len(skills()) >= 10, f"Expected 10+ skills, found {len(skills())}"


# ── Templates ─────────────────────────────────────────────────


def test_templates_exist():
    templates_dir = os.path.join(PLUGIN_DIR, "templates")
    assert exists(templates_dir), "templates/ missing"
    for tmpl in [
        "plan-template.md",
        "changelog-template.md",
        "progress-template.md",
        "review-template.md",
    ]:
        assert exists(os.path.join(templates_dir, tmpl)), f"Missing {tmpl}"


# ── Paths ─────────────────────────────────────────────────────


def test_paths_not_duplicated():
    for s in skills():
        lines = read(os.path.join(PLUGIN_DIR, s, "SKILL.md")).split("\n")
        matches = [
            l for l in lines if l.strip() == "Read shared paths from `config.md`."
        ]
        assert len(matches) == 1, (
            f"{s}/SKILL.md has {len(matches)} Paths lines (expected 1)"
        )


if __name__ == "__main__":
    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
                print(f"  PASS {name}")
            except Exception as e:
                failed += 1
                print(f"  FAIL {name}: {e}")
    print(f"\n{passed}/{passed + failed} passed")
    if failed:
        sys.exit(1)
