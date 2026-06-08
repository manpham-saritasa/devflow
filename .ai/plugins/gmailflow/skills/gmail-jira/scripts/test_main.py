"""Tests for gmail-jira pure helpers."""

import os
import sys
import unittest
from argparse import Namespace

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from errors import build_error
from main import assemble_proposal


class MainTests(unittest.TestCase):
    def test_build_error_has_expected_shape(self):
        result = build_error("Project key required.", ["--project"])
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["missing"], ["--project"])

    def test_assemble_proposal_keeps_warnings(self):
        args = Namespace(
            project="DEMOP",
            issue_key="",
            summary="[Field App] Report format issue",
            environment="Production",
            issue_type="Bug",
            component="Field App",
            estimate=0,
            description="",
            reply_body="Hi,\n\nItem: DEMOP-XXXX\n\nBest,\nQuan\n",
        )
        proposal = assemble_proposal(
            args,
            {"id": "1", "threadId": "2"},
            {
                "subject": "Subject line",
                "from": "Sender",
                "sender_email": "person@example.com",
                "message_id_header": "mid",
                "reply_to": "person@example.com",
                "body_text": "Problem line",
                "attachments": [],
            },
            {"id": "10", "name": "Bug"},
            {"id": "20", "name": "Field App"},
            None,
            {"sprint": None, "estimate": "customfield_2", "environment": None},
            ["active sprint", "environment"],
        )
        self.assertEqual(
            proposal["warnings"],
            ["Skipped Jira field: active sprint", "Skipped Jira field: environment"],
        )
        self.assertEqual(proposal["reply_preview"].count("DEMOP-XXXX"), 1)
        self.assertEqual(proposal["summary"], "[Field App] Report format issue")
        self.assertEqual(proposal["environment"], "Production")
        self.assertIsNone(proposal["estimate_hours"])
        self.assertIsNone(proposal["description"])


if __name__ == "__main__":
    unittest.main()
