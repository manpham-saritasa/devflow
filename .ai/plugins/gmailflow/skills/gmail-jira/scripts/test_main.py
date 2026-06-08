"""Tests for gmail-jira pure helpers."""

import os
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from errors import build_error
from main import _extract_email, _reply_recipients, assemble_proposal


class ReplyRecipientsTests(unittest.TestCase):
    def test_extract_bare_email(self):
        self.assertEqual(_extract_email("user@test.com"), "user@test.com")

    def test_extract_name_email(self):
        self.assertEqual(_extract_email("John Doe <john@test.com>"), "john@test.com")

    def test_extract_empty(self):
        self.assertEqual(_extract_email(""), "")

    def test_reply_includes_sender(self):
        result = _reply_recipients(
            "Alice <alice@test.com>",
            "me@test.com",
            "Bob <bob@test.com>",
            "",
        )
        self.assertIn("Alice", result["to"])
        self.assertIn("Bob", result["to"])

    def test_reply_excludes_self(self):
        result = _reply_recipients(
            "Alice <alice@test.com>",
            "me@test.com",
            "Me <me@test.com>, Bob <bob@test.com>",
            "Me <me@test.com>",
        )
        self.assertNotIn("me@test.com", result["to"].lower())
        self.assertNotIn("me@test.com", result["cc"].lower())
        self.assertIn("Alice", result["to"])
        self.assertIn("Bob", result["to"])

    def test_reply_includes_cc(self):
        result = _reply_recipients(
            "Alice <alice@test.com>",
            "me@test.com",
            "Bob <bob@test.com>",
            "Carol <carol@test.com>",
        )
        self.assertIn("Alice", result["to"])
        self.assertIn("Bob", result["to"])
        self.assertIn("Carol", result["cc"])

    def test_reply_dedup_cc_in_to(self):
        result = _reply_recipients(
            "Alice <alice@test.com>",
            "me@test.com",
            "Bob <bob@test.com>",
            "Bob <bob@test.com>, Carol <carol@test.com>",
        )
        self.assertNotIn("Bob", result["cc"])
        self.assertIn("Carol", result["cc"])

    def test_reply_empty_inputs(self):
        result = _reply_recipients("", "me@test.com", "", "")
        self.assertEqual(result["to"], "")
        self.assertEqual(result["cc"], "")


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
                "reply_to_all": {"to": "person@example.com", "cc": ""},
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

    def test_description_file_fallback(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write('{"type":"doc","version":1,"content":[]}')
            tmp_path = f.name
        try:
            a = Namespace(project="DEMOP", summary="T", environment="T", issue_type="Bug", component="A", estimate=0, description="", description_file=tmp_path, reply_body="")
            mi = {"subject":"S","from":"F","sender_email":"f@t.com","message_id_header":"m","reply_to":"f@t.com","reply_to_all":{"to":"f@t.com","cc":""},"body_text":"B","attachments":[]}
            r = assemble_proposal(a, {"id":"1","threadId":"2"}, mi, {"id":"1","name":"Bug"}, {"id":"2","name":"App"}, None, {"sprint":None,"estimate":None,"environment":None}, [])
            self.assertEqual(r["description"]["type"], "doc")
        finally:
            Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
