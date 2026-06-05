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
from main import main, parse_target


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


class JiraUtilsTests(unittest.TestCase):
    def test_format_seconds(self) -> None:
        from jira.jira_utils import JiraUtils

        self.assertEqual(JiraUtils.format_seconds(None), "None")
        self.assertEqual(JiraUtils.format_seconds(0), "0m")
        self.assertEqual(JiraUtils.format_seconds(1800), "30m")
        self.assertEqual(JiraUtils.format_seconds(3600), "1h")
        self.assertEqual(JiraUtils.format_seconds(7200), "2h")
        self.assertEqual(JiraUtils.format_seconds(5400), "1h 30m")

    def test_html_to_text(self) -> None:
        from jira.jira_utils import JiraUtils

        self.assertEqual(JiraUtils.html_to_text("<p>Hello</p>"), "Hello")
        self.assertIn("line1", JiraUtils.html_to_text("<p>line1</p><p>line2</p>"))
        self.assertEqual(
            JiraUtils.html_to_text("<b>bold</b> &amp; <i>italic</i>"),
            "bold & italic",
        )
        self.assertEqual(JiraUtils.html_to_text("a<br>b"), "a\nb")
        self.assertEqual(JiraUtils.html_to_text("<li>item</li>"), "- item")

    def test_adf_to_text_paragraph(self) -> None:
        from jira.jira_utils import JiraUtils

        node = {
            "type": "paragraph",
            "content": [{"type": "text", "text": "Hello world"}],
        }
        self.assertIn("Hello world", JiraUtils.adf_to_text(node))

    def test_adf_to_text_mention(self) -> None:
        from jira.jira_utils import JiraUtils

        node = {"type": "mention", "attrs": {"text": "John"}}
        self.assertEqual(JiraUtils.adf_to_text(node), "@John")

    def test_adf_to_text_list(self) -> None:
        from jira.jira_utils import JiraUtils

        node = [
            {"type": "paragraph", "content": [{"type": "text", "text": "A"}]},
            {"type": "paragraph", "content": [{"type": "text", "text": "B"}]},
        ]
        result = JiraUtils.adf_to_text(node)
        self.assertIn("A", result)
        self.assertIn("B", result)

    def test_extract_sprint_from_list(self) -> None:
        from jira.jira_utils import JiraUtils

        fields = {"customfield_10006": [{"name": "Sprint 1"}, {"name": "Sprint 2"}]}
        self.assertEqual(
            JiraUtils.extract_sprint(fields, "customfield_10006"), "Sprint 2"
        )

    def test_extract_sprint_from_dict(self) -> None:
        from jira.jira_utils import JiraUtils

        fields = {"customfield_10006": {"name": "Active Sprint"}}
        self.assertEqual(
            JiraUtils.extract_sprint(fields, "customfield_10006"), "Active Sprint"
        )

    def test_extract_sprint_missing(self) -> None:
        from jira.jira_utils import JiraUtils

        self.assertIsNone(JiraUtils.extract_sprint({}, "customfield_10006"))
        self.assertIsNone(
            JiraUtils.extract_sprint({"customfield_10006": []}, "customfield_10006")
        )


class GithubUtilsTests(unittest.TestCase):
    def test_login(self) -> None:
        from github.github_utils import GithubUtils

        self.assertEqual(GithubUtils.login(None), "unknown")
        self.assertEqual(GithubUtils.login({}), "unknown")
        self.assertEqual(GithubUtils.login({"login": "alice"}), "alice")

    def test_yes_no(self) -> None:
        from github.github_utils import GithubUtils

        self.assertEqual(GithubUtils.yes_no(True), "Yes")
        self.assertEqual(GithubUtils.yes_no(False), "No")
        self.assertEqual(GithubUtils.yes_no(None), "No")

    def test_date_or(self) -> None:
        from github.github_utils import GithubUtils

        self.assertEqual(GithubUtils.date_or(None), "n/a")
        self.assertEqual(GithubUtils.date_or("2024-01-01"), "2024-01-01")
        self.assertEqual(GithubUtils.date_or(None, "fallback"), "fallback")

    def test_should_skip_file(self) -> None:
        from github.github_utils import GithubUtils

        self.assertTrue(GithubUtils.should_skip_file(None))
        self.assertTrue(GithubUtils.should_skip_file(".claude/config"))
        self.assertTrue(GithubUtils.should_skip_file("readme.md"))
        self.assertTrue(GithubUtils.should_skip_file(".gitignore"))
        self.assertFalse(GithubUtils.should_skip_file("src/main.py"))
        self.assertFalse(GithubUtils.should_skip_file("config.json"))

    def test_format_bullets_empty(self) -> None:
        from github.github_utils import GithubUtils

        self.assertEqual(GithubUtils.format_bullets([], lambda x: "-"), "_(none)_")

    def test_format_bullets_populated(self) -> None:
        from github.github_utils import GithubUtils

        items = [{"name": "A"}, {"name": "B"}]
        result = GithubUtils.format_bullets(items, lambda x: f"- {x['name']}")
        self.assertEqual(result, "- A\n- B")


class JiraHttpClientTests(unittest.TestCase):
    def test_safe_nav_returns_value(self) -> None:
        from jira.http_client import JiraHttpClient

        data = {"status": {"name": "Done"}}
        self.assertEqual(JiraHttpClient.safe_nav(data, "status", "name"), "Done")

    def test_safe_nav_returns_default_on_missing(self) -> None:
        from jira.http_client import JiraHttpClient

        self.assertEqual(JiraHttpClient.safe_nav({}, "status", "name"), "?")
        self.assertEqual(
            JiraHttpClient.safe_nav({"status": {}}, "status", "name", default="N/A"),
            "N/A",
        )

    def test_safe_nav_on_nondict(self) -> None:
        from jira.http_client import JiraHttpClient

        self.assertEqual(JiraHttpClient.safe_nav({"x": 1}, "x", "y"), "?")


class JiraTaskTests(unittest.TestCase):
    def _task(self, **kwargs: object) -> JiraTask:
        defaults: dict[str, object] = {
            "key": "APP-1",
            "summary": "Test",
            "status": "To Do",
            "priority": "Medium",
            "issuetype": "Task",
            "assignee": "Me",
            "reporter": "You",
            "labels": [],
            "components": [],
            "fix_versions": [],
            "created": "2024-01-01",
            "updated": "2024-01-01",
            "due_date": "None",
            "resolution": "Unresolved",
            "resolution_date": "None",
            "description_raw": None,
            "description_text": "",
        }
        defaults.update(kwargs)
        return JiraTask(**defaults)  # type: ignore[arg-type]

    def test_browse_url(self) -> None:
        self.assertEqual(
            JiraTask.browse_url("https://jira.example.com", "APP-1"),
            "https://jira.example.com/browse/APP-1",
        )

    def test_epic_md_with_epic(self) -> None:
        task = self._task(epic_key="EP-1", epic_summary="Big epic")
        result = task.epic_md("https://j.example.com")
        self.assertIn("EP-1", result)
        self.assertIn("Big epic", result)

    def test_epic_md_no_epic(self) -> None:
        task = self._task()
        self.assertEqual(task.epic_md(), "None")

    def test_parent_md_with_parent(self) -> None:
        task = self._task(
            parent_key="APP-5", parent_summary="Parent task", parent_type="Story"
        )
        result = task.parent_md("https://j.example.com")
        self.assertIn("APP-5", result)
        self.assertIn("Story", result)

    def test_parent_md_no_parent(self) -> None:
        self.assertEqual(self._task().parent_md(), "None")

    def test_subtasks_md_empty(self) -> None:
        self.assertEqual(self._task().subtasks_md(), " None")

    def test_subtasks_md_with_items(self) -> None:
        task = self._task(
            subtasks_detail=[
                SubtaskInfo(
                    key="APP-2",
                    summary="Sub A",
                    status="Done",
                    issue_type="Sub-task",
                    url="http://j/browse/APP-2",
                ),
                SubtaskInfo(
                    key="APP-3",
                    summary="Sub B",
                    status="To Do",
                    issue_type="Sub-task",
                    url="http://j/browse/APP-3",
                ),
            ]
        )
        result = task.subtasks_md("http://j")
        self.assertIn("APP-2", result)
        self.assertIn("APP-3", result)
        self.assertIn("Done", result)

    def test_related_tasks_md_empty(self) -> None:
        self.assertIn("none", self._task().related_tasks_md())

    def test_related_tasks_md_with_links(self) -> None:
        task = self._task(
            linked_issues=[
                {
                    "key": "APP-9",
                    "summary": "Related",
                    "type": "blocks",
                    "status": "Done",
                },
            ]
        )
        result = task.related_tasks_md("https://j.example.com")
        self.assertIn("APP-9", result)
        self.assertIn("blocks", result)

    def test_tags_md_no_tags(self) -> None:
        self.assertEqual(self._task().tags_md(), "None")

    def test_tags_md_with_tags_no_field_id(self) -> None:
        task = self._task(tags=["alpha", "beta"])
        self.assertEqual(task.tags_md(), "alpha, beta")

    def test_tags_md_with_field_id(self) -> None:
        task = self._task(tags=["multi-tenant"])
        result = task.tags_md("https://j.example.com", "customfield_13351")
        self.assertIn("multi-tenant", result)
        self.assertIn("cf%5B13351%5D", result)

    def test_component_str_empty(self) -> None:
        self.assertEqual(self._task().component_str, "None")

    def test_component_str_populated(self) -> None:
        task = self._task(components=["API", "Backend"])
        self.assertEqual(task.component_str, "API, Backend")

    def test_attachments_md_empty(self) -> None:
        self.assertIn("none", self._task().attachments_md())

    def test_url_property(self) -> None:
        self.assertEqual(self._task().url, "")

    def test_to_json_record_resolution_unresolved(self) -> None:
        task = self._task()
        record = task.to_json_record("dev/tasks", "https://j.example.com")
        self.assertEqual(record["resolution"], "None")
        self.assertIsNone(record["resolution_date"])
        self.assertIsNone(record["epic"])
        self.assertIsNone(record["parent"])


class ParseTargetTests(unittest.TestCase):
    def test_full_key(self) -> None:
        project, issue_id = parse_target("APP-2100", "APP")
        self.assertEqual(project, "APP")
        self.assertEqual(issue_id, 2100)

    def test_numeric_only(self) -> None:
        project, issue_id = parse_target("42", "APP")
        self.assertEqual(project, "APP")
        self.assertEqual(issue_id, 42)

    def test_lowercase_key(self) -> None:
        project, issue_id = parse_target("app-99", "APP")
        self.assertEqual(project, "APP")
        self.assertEqual(issue_id, 99)

    def test_invalid_format_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_target("not-a-key", "APP")
        with self.assertRaises(ValueError):
            parse_target("", "APP")

    def test_wrong_project_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_target("OTHER-1", "APP")


if __name__ == "__main__":
    unittest.main()
