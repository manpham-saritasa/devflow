import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("JIRA_URL", "https://example.atlassian.net")
os.environ.setdefault("JIRA_EMAIL", "test@example.com")
os.environ.setdefault("JIRA_API_TOKEN", "dummy-token")
os.environ.setdefault("JIRA_PROJECT_KEY", "APP")

from dto.comment import Comment
from dto.jira_task import JiraTask
from dto.subtask_info import SubtaskInfo
from jira.config import REPO_ROOT, load_app_config
from jira.fetcher import build_task_json, render_raw_md
from jira.sync_state import add_not_found_id, load_not_found_ids, load_state, save_state
from jira.task_fetcher import JiraTaskFetcher
from main import main


class ConfigTests(unittest.TestCase):
    def test_load_app_config_rejects_paths_outside_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "download_path": "../outside",
                        "sync_state_path": "result/sync-state.json",
                        "not_found_state_path": "result/not-found.json",
                        "template_paths": ["templates/raw-template.md"],
                        "custom_fields": {},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError, "must stay within the repository root"
            ):
                load_app_config(config_path)

    def test_load_app_config_accepts_repo_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "download_path": "dev/tasks",
                        "sync_state_path": "result/sync-state.json",
                        "not_found_state_path": "result/not-found.json",
                        "template_paths": ["templates/raw-template.md"],
                        "custom_fields": {"epic_link": "customfield_1"},
                    }
                ),
                encoding="utf-8",
            )

            config_dir = config_path.parent
            with patch("jira.config.REPO_ROOT", config_dir):
                app_config = load_app_config(config_path)

            self.assertEqual(
                app_config.download_path, (config_dir / "dev/tasks").resolve()
            )
            self.assertEqual(
                app_config.sync_state_path,
                (config_dir / "result/sync-state.json").resolve(),
            )


class SyncStateTests(unittest.TestCase):
    def test_load_state_returns_defaults_for_missing_or_invalid_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "sync-state.json"

            self.assertEqual(
                load_state(state_path, "APP"),
                {"max_downloaded_id": 0, "last_sync_at": None},
            )

            state_path.write_text(
                '{"APP": {"max_downloaded_id": "bad", "last_sync_at": 123}}',
                encoding="utf-8",
            )

            self.assertEqual(
                load_state(state_path, "APP"),
                {"max_downloaded_id": 0, "last_sync_at": None},
            )

    def test_save_state_creates_parent_directory_and_persists_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "nested" / "sync-state.json"

            save_state(state_path, "APP", 42)

            self.assertTrue(state_path.exists())
            loaded = load_state(state_path, "APP")
            self.assertEqual(loaded["max_downloaded_id"], 42)
            self.assertIsInstance(loaded["last_sync_at"], str)

    def test_not_found_ids_are_deduplicated_and_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            not_found_path = Path(temp_dir) / "nested" / "tasks-not-found.txt"

            add_not_found_id(not_found_path, "APP", 7)
            add_not_found_id(not_found_path, "APP", 3)
            add_not_found_id(not_found_path, "APP", 7)

            ids = load_not_found_ids(not_found_path, "APP")
            self.assertEqual(ids, {"APP-7", "APP-3"})
            content = not_found_path.read_text(encoding="utf-8")
            self.assertIn("APP-3", content)
            self.assertIn("APP-7", content)


class RenderTests(unittest.TestCase):
    """Test rendering via JiraTask (jira_fetcher.py path — the production path)."""

    def _sample_task(self) -> JiraTask:
        return JiraTask(
            key="APP-123",
            summary="Add invoice sync endpoint",
            status="In Progress",
            priority="High",
            issuetype="Story",
            assignee="Alice",
            reporter="Bob",
            labels=["backend", "api"],
            components=["Billing"],
            fix_versions=["1.2.0"],
            created="2024-01-02",
            updated="2024-01-03",
            due_date="2024-01-10",
            resolution="Unresolved",
            resolution_date="None",
            description_raw=None,
            description_text="Implement API endpoint and coordinate with APP-88.",
            estimated_seconds=7200,
            spent_seconds=1800,
            epic_key="APP-10",
            epic_summary="Invoice improvements epic",
            story_points="5",
            subtask_keys=["APP-124"],
            subtasks_detail=[
                SubtaskInfo(
                    key="APP-124",
                    summary="Add API client",
                    status="Done",
                    issue_type="Sub-task",
                    url="https://example.atlassian.net/browse/APP-124",
                )
            ],
            linked_issues=[
                {
                    "key": "APP-77",
                    "summary": "Prepare release notes",
                    "type": "blocks",
                    "status": "To Do",
                }
            ],
            comments=[
                Comment(
                    author="Carol",
                    created="2024-01-04",
                    body_text="Please verify APP-77 before release.",
                )
            ],
        )

    def test_render_raw_md_includes_key_sections(self) -> None:
        task = self._sample_task()
        content = render_raw_md(
            task,
            jira_url="https://example.atlassian.net",
            tags_field_id="customfield_13351",
        )

        self.assertIn("# APP-123", content)
        self.assertIn("Add invoice sync endpoint", content)
        self.assertIn("## Related Tasks", content)
        self.assertIn("APP-77", content)
        self.assertIn("## Comments", content)
        self.assertIn("Carol", content)
        self.assertIn("In Progress", content)
        self.assertIn("Story", content)
        self.assertIn("High", content)

    def test_build_task_json_contains_structured_fields(self) -> None:
        task = self._sample_task()
        record = build_task_json(
            task,
            download_path_rel="dev/tasks",
            jira_url="https://example.atlassian.net",
        )

        self.assertEqual(record["task_key"], "APP-123")
        self.assertEqual(record["estimated"], "2h")
        self.assertEqual(record["spent"], "30m")
        self.assertEqual(record["components"], ["Billing"])
        self.assertEqual(record["labels"], ["backend", "api"])
        self.assertEqual(record["paths"]["task_json"], "dev/tasks/APP-123/task.json")
        self.assertEqual(record["subtasks"][0]["key"], "APP-124")
        self.assertEqual(record["comments"][0]["author"], "Carol")
        self.assertEqual(record["story_points"], "5")
        self.assertIsNotNone(record["epic"])
        self.assertEqual(record["epic"]["key"], "APP-10")

    def test_task_with_minimal_fields_renders_without_errors(self) -> None:
        task = JiraTask(
            key="APP-999",
            summary="Minimal task",
            status="To Do",
            priority="Medium",
            issuetype="Task",
            assignee="Unassigned",
            reporter="Unknown",
            labels=[],
            components=[],
            fix_versions=[],
            created="2024-06-01",
            updated="2024-06-01",
            due_date="None",
            resolution="Unresolved",
            resolution_date="None",
            description_raw=None,
            description_text="",
            estimated=None,
            spent=None,
        )

        content = render_raw_md(task)
        self.assertIn("# APP-999", content)
        self.assertIn("Minimal task", content)

        record = build_task_json(task, download_path_rel="dev/tasks")
        self.assertEqual(record["task_key"], "APP-999")
        self.assertEqual(record["estimated"], "None")
        self.assertEqual(record["epic"], None)
        self.assertEqual(record["subtasks"], [])


class MainTests(unittest.TestCase):
    def test_main_skips_known_missing_issue_without_fetching_jira(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            config_path = repo_root / "config.json"
            download_path = repo_root / "dev" / "tasks"
            sync_state_path = repo_root / "result" / "sync-state.json"
            not_found_state_path = repo_root / "result" / "not-found.json"

            config_path.write_text(
                json.dumps(
                    {
                        "download_path": "dev/tasks",
                        "sync_state_path": "result/sync-state.json",
                        "not_found_state_path": "result/not-found.json",
                        "template_paths": ["templates/raw-template.md"],
                        "custom_fields": {},
                    }
                ),
                encoding="utf-8",
            )
            download_path.mkdir(parents=True, exist_ok=True)
            add_not_found_id(not_found_state_path, "APP", 3)

            stdout = io.StringIO()
            with (
                patch(
                    "sys.argv",
                    ["main.py", "--config", str(config_path), "--start", "1"],
                ),
                patch.object(JiraTaskFetcher, "get_max_issue_id", return_value=3),
                patch.object(JiraTaskFetcher, "fetch") as fetch_mock,
                patch("main.load_not_found_ids", return_value={"APP-3"}),
                patch("jira.config.REPO_ROOT", repo_root),
                patch("main.REPO_ROOT", repo_root),
                redirect_stdout(stdout),
            ):
                main()

            output = stdout.getvalue()
            self.assertEqual(fetch_mock.call_count, 2)
            self.assertIn("APP-3: known missing - skip", output)
            self.assertIn("Not found:   1", output)


if __name__ == "__main__":
    unittest.main()
