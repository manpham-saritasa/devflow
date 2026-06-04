import os
import sys
from unittest import TestCase, main

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from candidate import Candidate
from context import RuntimeContext
from output import rank_candidates


def make_runtime(role="mixed"):
    return RuntimeContext(
        project="TEST",
        role=role,
        check_pr=False,
        stage_groups={
            "review": ["In Review", "Code Review"],
            "qa": ["In QA"],
            "active": ["In Progress"],
            "blocked": ["Blocked"],
        },
        window_hours=24,
        jira_domain="test",
        prefer_projects=[],
    )


def make_candidate(key, evidence, status="In Progress", logged_seconds=0):
    c = Candidate(key, f"Summary {key}", status, "High", "Assignee")
    for tag in evidence:
        c.evidence.add(tag)
    c.logged_seconds = logged_seconds
    return c


class RankingTests(TestCase):
    def test_mixed_2_strong_signals_top(self):
        """mixed: 2+ strong signals > 1 strong signal"""
        runtime = make_runtime("mixed")
        a = make_candidate("KEY-1", {"comment", "transition"})
        b = make_candidate("KEY-2", {"comment"})
        ranked = rank_candidates({a.key: a, b.key: b}, runtime)
        self.assertEqual(ranked[0].key, "KEY-1")

    def test_mixed_1_strong_beats_updated_only(self):
        """mixed: 1 strong signal > updated-only"""
        runtime = make_runtime("mixed")
        a = make_candidate("KEY-1", {"comment"})
        b = make_candidate("KEY-2", {"updated"})
        ranked = rank_candidates({a.key: a, b.key: b}, runtime)
        self.assertEqual(ranked[0].key, "KEY-1")

    def test_not_logged_before_logged(self):
        """within same bucket, not logged > logged"""
        runtime = make_runtime("mixed")
        a = make_candidate("KEY-1", {"comment"}, logged_seconds=0)
        b = make_candidate("KEY-2", {"comment"}, logged_seconds=600)
        ranked = rank_candidates({a.key: a, b.key: b}, runtime)
        self.assertEqual(ranked[0].key, "KEY-1")

    def test_dev_pr_beats_git(self):
        """dev: PR activity > git activity"""
        runtime = make_runtime("dev")
        runtime = RuntimeContext(
            project="TEST",
            role="dev",
            check_pr=True,
            stage_groups={},
            window_hours=24,
            jira_domain="test",
            prefer_projects=[],
        )
        a = make_candidate("KEY-1", {"pr"})
        b = make_candidate("KEY-2", {"git"})
        ranked = rank_candidates({a.key: a, b.key: b}, runtime)
        self.assertEqual(ranked[0].key, "KEY-1")

    def test_qa_stage_qa_comment_beats_other_comment(self):
        """qa: QA-stage comment > non-QA-stage comment"""
        runtime = RuntimeContext(
            project="TEST",
            role="qa",
            check_pr=False,
            stage_groups={"qa": ["In QA"]},
            window_hours=24,
            jira_domain="test",
            prefer_projects=[],
        )
        a = make_candidate("KEY-1", {"comment"}, status="In QA")
        b = make_candidate("KEY-2", {"comment"}, status="In Progress")
        ranked = rank_candidates({a.key: a, b.key: b}, runtime)
        self.assertEqual(ranked[0].key, "KEY-1")


if __name__ == "__main__":
    main()
