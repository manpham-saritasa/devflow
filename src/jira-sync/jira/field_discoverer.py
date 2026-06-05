"""Discovers and displays Jira custom field IDs for config.json setup."""

from typing import Any

from jira.http_client import JiraHttpClient


class JiraFieldDiscoverer:
    """Fetches and prints Jira custom field names and IDs."""

    def __init__(
        self, http: JiraHttpClient, project_key: str, custom_fields: dict[str, str]
    ) -> None:
        self._http = http
        self._project_key = project_key
        self._custom_fields = custom_fields

    def discover(self, show_all: bool = False) -> None:
        pk = self._project_key
        print(f"Discovering custom fields for project '{pk}'...\n")
        custom_names = self._fetch_field_names()
        if not custom_names:
            print("No issues found in project. Cannot discover fields.")
            return
        if show_all:
            self._print_all_fields(custom_names)
            return
        matched_ids = self._print_configured_fields(custom_names)
        self._print_unmatched_fields(custom_names, matched_ids)

    @staticmethod
    def _print_all_fields(custom_names: dict[str, str]) -> None:
        print(f"All {len(custom_names)} custom fields:\n")
        for field_id, field_name in sorted(custom_names.items()):
            print(f"  {field_name}\n  -> {field_id}\n")

    def _print_configured_fields(self, custom_names: dict[str, str]) -> set[str]:
        configured = self._custom_fields
        if not configured:
            return set()
        matched: set[str] = set()
        print("Configured custom fields:\n")
        for config_key, config_value in configured.items():
            if not config_value:
                print(f'  "{config_key}": "",  # NOT SET')
                continue
            if config_value.startswith("customfield_"):
                name = custom_names.get(config_value, "unknown")
                print(f'  "{config_key}": "{config_value}",  # {name}')
                matched.add(config_value)
            else:
                found = False
                for field_id, field_name in sorted(custom_names.items()):
                    if field_name.lower() == config_value.lower():
                        print(f'  "{config_key}": "{field_id}",  # {field_name}')
                        matched.add(field_id)
                        found = True
                        break
                if not found:
                    print(f'  "{config_key}": "",  # NOT FOUND: "{config_value}"')
        print()
        return matched

    @staticmethod
    def _print_unmatched_fields(
        custom_names: dict[str, str], matched_ids: set[str]
    ) -> None:
        unmatched = {
            fid: fname
            for fid, fname in sorted(custom_names.items())
            if fid not in matched_ids
        }
        if not unmatched:
            return
        label = (
            "Other custom fields"
            if matched_ids
            else f"All {len(unmatched)} custom fields"
        )
        print(f"{label}:\n")
        for field_id, field_name in unmatched.items():
            print(f"  # {field_name}\n  # -> {field_id}\n")

    def _fetch_field_names(self) -> dict[str, str]:
        pk = self._project_key
        data = self._http.post_json(
            f"{self._http.base_url}/rest/api/3/search/jql",
            {
                "jql": f"project = {pk} ORDER BY created DESC",
                "maxResults": 1,
                "fields": ["summary"],
            },
        )
        issues = data.get("issues", [])
        if not issues:
            return {}
        sample_key = issues[0]["key"]
        names = (
            self._http.get(f"{self._http.base_url}/rest/api/3/issue/{sample_key}").get(
                "names"
            )
            or {}
        )
        result: dict[str, str] = {}
        for field_id, field_name in names.items():
            if field_id.startswith("customfield_"):
                result[field_id] = str(field_name)
        return result
