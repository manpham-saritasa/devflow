"""Tests for jira-create pure flow helpers."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import cast

_JIRAFLOW_ROOT = Path(__file__).resolve().parents[4]
if str(_JIRAFLOW_ROOT) not in sys.path:
    sys.path.insert(0, str(_JIRAFLOW_ROOT))

from shared.common import JiraCreateConfigStore
from shared.create_flow import (
    add_custom_field,
    build_issue_fields,
    choose_scrum_board,
    discover_fields,
)
from shared.jira_api import JiraClient


class FakeJiraClient:
    """Tiny Jira client stub for field discovery tests."""

    def __init__(self, fields):
        """Store createmeta-style fields payload."""
        self.fields = fields
        self.calls = 0

    def get_create_meta(self, project_key, issue_type_id):
        """Return one createmeta payload and count calls."""
        self.calls += 1
        return {
            "projects": [
                {
                    "issuetypes": [
                        {
                            "fields": self.fields,
                        }
                    ]
                }
            ]
        }


class CreateFlowTests(unittest.TestCase):
    def test_choose_scrum_board_prefers_matching_project(self):
        boards = {
            "values": [
                {"id": 1, "type": "kanban", "location": {"projectKey": "DEMOP"}},
                {"id": 2, "type": "scrum", "location": {"projectKey": "OTHER"}},
                {"id": 3, "type": "scrum", "location": {"projectKey": "DEMOP"}},
            ]
        }
        result = choose_scrum_board(boards, "DEMOP")
        self.assertEqual(result["id"], 3)

    def test_add_custom_field_skips_empty_field_id(self):
        fields = {"summary": "Test"}
        add_custom_field(fields, "", 4)
        self.assertEqual(fields, {"summary": "Test"})

    def test_build_issue_fields_adds_optional_custom_fields(self):
        proposal = {
            "project": "DEMOP",
            "summary": "Test summary",
            "description": {"type": "doc"},
            "issue_type": {"id": "10001"},
            "component": {"id": "20001"},
            "jira_fields": {
                "sprint": "customfield_1",
                "estimate": "customfield_2",
                "environment": "customfield_3",
            },
            "sprint": {"id": 555},
            "estimate_hours": 4,
            "environment": "Production LIMS",
        }
        fields = build_issue_fields(proposal)
        self.assertEqual(fields["project"]["key"], "DEMOP")
        self.assertEqual(fields["components"][0]["id"], "20001")
        self.assertEqual(fields["customfield_1"], 555)
        self.assertEqual(fields["customfield_2"], 4)
        self.assertEqual(fields["customfield_3"], "Production LIMS")

    def test_build_issue_fields_skips_missing_custom_fields(self):
        proposal = {
            "project": "DEMOP",
            "summary": "Test summary",
            "description": {"type": "doc"},
            "issue_type": {"id": "10001"},
            "component": {"id": "20001"},
            "jira_fields": {"sprint": "", "estimate": None},
            "sprint": {"id": 555},
            "estimate_hours": 4,
        }
        fields = build_issue_fields(proposal)
        self.assertNotIn("", fields)
        self.assertEqual(len(fields), 5)

    def test_discover_fields_uses_cache_when_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            store = JiraCreateConfigStore(repo_root)
            store.save_jira_fields(
                {
                    "DEMOP": {
                        "sprint": "customfield_1",
                        "estimate": "customfield_2",
                        "environment": "customfield_3",
                    }
                }
            )
            client = FakeJiraClient({})
            result, missing = discover_fields(
                store,
                cast(JiraClient, client),
                "DEMOP",
                "10001",
            )
            self.assertEqual(result["sprint"], "customfield_1")
            self.assertEqual(missing, [])
            self.assertEqual(client.calls, 0)

    def test_discover_fields_reads_createmeta_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            store = JiraCreateConfigStore(repo_root)
            client = FakeJiraClient(
                {
                    "customfield_1": {"name": "Sprint"},
                    "customfield_2": {"name": "Development Estimate"},
                    "customfield_3": {"name": "Environment"},
                }
            )
            result, missing = discover_fields(
                store,
                cast(JiraClient, client),
                "DEMOP",
                "10001",
            )
            self.assertEqual(result["sprint"], "customfield_1")
            self.assertEqual(result["estimate"], "customfield_2")
            self.assertEqual(result["environment"], "customfield_3")
            self.assertEqual(missing, [])
            self.assertEqual(client.calls, 1)
            saved = store.load_jira_fields()
            self.assertEqual(saved["DEMOP"]["estimate"], "customfield_2")


if __name__ == "__main__":
    unittest.main()
