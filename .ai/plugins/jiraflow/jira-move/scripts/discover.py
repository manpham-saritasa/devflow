"""Discover - explore Jira workflow, record transitions, save to project config."""

import json
import urllib.error
import urllib.request

DEAD_END_STATUSES = {"Cancelled", "Blocked", "Complete", "Completed", "Completed."}


def _is_dead_end(to_name, milestone_name, milestones):
    """Dead-end statuses are skipped unless targeting the complete milestone."""
    if to_name not in DEAD_END_STATUSES:
        return False
    to_ms = milestones.status_to_milestone(to_name)
    return to_ms != milestone_name


class Discoverer:
    def __init__(self, domain, auth, milestones, pipeline):
        self.domain = domain
        self.auth = auth
        self.milestones = milestones
        self.pipeline = pipeline

    def run(self, key):
        project_key = key.split("-")[0]
        config = load_config(project_key) or {"milestones": {}, "transitions": {}}
        original_status = self._get_status(key)

        print(f"## Discovering workflow for {project_key} using {key}\n")
        print(f"Original status: {original_status}\n")
        self._show_statuses(project_key)

        discovered_milestones = self._discover_stages(key, config)
        config["milestones"] = discovered_milestones
        save_config(project_key, config, self.milestones.pipeline)

        self._print_summary(config)
        self._maybe_restore(key, config, original_status)

    def _discover_stages(self, key, config):
        project_key = key.split("-")[0]
        visited = set()
        discovered_milestones = {}
        stage = 0

        for milestone_name in self.milestones.pipeline:
            stage += 1
            current = self._get_status(key)
            current_ms = self.milestones.status_to_milestone(current) or current
            print(
                f"### Stage {stage}: Milestone '{milestone_name}' (current: {current} [{current_ms}])"
            )

            if current not in visited:
                transitions = self._get_transitions(key)
                config["transitions"][current] = {
                    str(t["id"]): t["to"]["name"] for t in transitions
                }
                visited.add(current)
                current_ms = self.milestones.status_to_milestone(current)
                if current_ms:
                    discovered_milestones.setdefault(current_ms, [])
                    if current not in discovered_milestones[current_ms]:
                        discovered_milestones[current_ms].append(current)
                self._print_transitions(transitions)

            if current_ms == milestone_name:
                print(f"  [OK] Already at milestone '{milestone_name}'\n")
                continue

            if self.milestones.is_last(milestone_name):
                continue

            trans_map = config["transitions"].get(current, {})
            tid = self._find_transition_to_milestone(trans_map, milestone_name)
            if not tid:
                tid = self._fallback_transition(key, trans_map, visited, milestone_name)
                if tid == "used":
                    continue
            if not tid:
                print(
                    f"  [NO] No transition to milestone '{milestone_name}' from '{current}'"
                )
                print(f"  -> Move '{key}' manually, then re-run --discover.")
                save_config(project_key, config, self.milestones.pipeline)
                return None

            try:
                self._execute(key, tid)
                new = self._get_status(key)
                print(f"  [OK] Moved to {new}\n")
            except RuntimeError as e:
                print(f"  [STOP] Can't move: {e}")
                print(
                    f"  -> Move '{key}' to milestone '{milestone_name}' manually, then re-run --discover."
                )
                save_config(project_key, config, self.milestones.pipeline)
                return None

        current = self._get_status(key)
        if current not in visited:
            transitions = self._get_transitions(key)
            config["transitions"][current] = {
                str(t["id"]): t["to"]["name"] for t in transitions
            }
            visited.add(current)

        self._fill_milestone_mappings(config, discovered_milestones)

        return discovered_milestones

    def _fill_milestone_mappings(self, config, discovered_milestones):
        """Add milestone mappings for source statuses and their target statuses."""
        for status_name, transitions in list(config["transitions"].items()):
            ms = self.milestones.status_to_milestone(status_name)
            if ms and ms not in discovered_milestones:
                discovered_milestones[ms] = [status_name]
            for to_name in transitions.values():
                ms = self.milestones.status_to_milestone(to_name)
                if ms and ms not in discovered_milestones:
                    discovered_milestones[ms] = [to_name]

    def _fallback_transition(self, key, trans_map, visited, milestone_name):
        """Try unvisited transitions to known milestones. Skip dead ends."""
        for t_id, to_name in trans_map.items():
            if _is_dead_end(to_name, milestone_name, self.milestones):
                continue
            to_ms = self.milestones.status_to_milestone(to_name)
            if to_ms and to_name not in visited:
                try:
                    print(f"  -> Trying {to_name} ({to_ms})...")
                    self._execute(key, t_id)
                    new = self._get_status(key)
                    print(f"  [OK] Moved to {new}\n")
                    return "used"
                except RuntimeError:
                    continue
        return None

    def _print_summary(self, config):
        total = sum(len(t) for t in config["transitions"].values())
        visited = list(config["transitions"].keys())
        print(f"\n### Summary - {len(visited)} states, {total} transitions")
        for status_name in sorted(visited):
            ms = self.milestones.status_to_milestone(status_name) or "-"
            trans_map = config["transitions"].get(status_name, {})
            if trans_map:
                to_list = ", ".join(trans_map.values())
                print(f"  {status_name}  [{ms}] -> {to_list}")

    def _maybe_restore(self, key, config, original_status):
        current = self._get_status(key)
        if current.lower() != original_status.lower():
            print(f"\n[RESTORE] Restoring {key} to {original_status}...")
            self._restore(key, config, original_status)

    def _get_status(self, key):
        data = self._jira_get(f"/issue/{key}?fields=status")
        return data["fields"]["status"]["name"]

    def _get_transitions(self, key):
        return self._jira_get(f"/issue/{key}/transitions")["transitions"]

    def _jira_get(self, path):
        req = urllib.request.Request(
            f"https://{self.domain}.atlassian.net/rest/api/3{path}"
        )
        req.add_header("Authorization", f"Basic {self.auth}")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _execute(self, key, tid):
        body = json.dumps({"transition": {"id": tid}}).encode()
        req = urllib.request.Request(
            f"https://{self.domain}.atlassian.net/rest/api/3/issue/{key}/transitions",
            data=body,
        )
        req.add_header("Authorization", f"Basic {self.auth}")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status != 204:
                    json.loads(resp.read())
        except urllib.error.HTTPError as e:
            err_body = json.loads(e.read().decode())
            errors = err_body.get("errors", {})
            error_msgs = err_body.get("errorMessages", [])
            if isinstance(errors, dict) and errors:
                msg = f"Required: {', '.join(errors.keys())}"
            elif error_msgs:
                msg = "; ".join(error_msgs)
            else:
                msg = str(err_body)
            raise RuntimeError(msg) from e

    def _find_transition_to_milestone(self, trans_map, milestone_name):
        for tid, to_name in trans_map.items():
            if _is_dead_end(to_name, milestone_name, self.milestones):
                continue
            to_ms = self.milestones.status_to_milestone(to_name)
            if to_ms == milestone_name:
                return tid
        return None

    def _show_statuses(self, project_key):
        try:
            data = self._jira_get(f"/project/{project_key}/statuses")
            statuses = set()
            for issue_type in data:
                for s in issue_type.get("statuses", []):
                    statuses.add(s["name"])
            if statuses:
                print(f"### Project Statuses ({len(statuses)}):")
                for s in sorted(statuses):
                    ms = self.milestones.status_to_milestone(s) or "-"
                    print(f"  - {s}  [{ms}]")
                print()
        except Exception:
            pass

    def _restore(self, key, config, original_status):
        current = self._get_status(key)
        max_steps = 10
        while current.lower() != original_status.lower() and max_steps > 0:
            max_steps -= 1
            trans_map = config["transitions"].get(current, {})
            tid = None
            for t, name in trans_map.items():
                if name.lower() == original_status.lower():
                    tid = t
                    break
            if not tid:
                for t, name in trans_map.items():
                    if name.lower() == "ready for development":
                        tid = t
                        break
            if not tid:
                print(f"  [WARN] No reverse path from {current}")
                break
            self._execute(key, tid)
            current = self._get_status(key)
            print(f"  -> {current}")
        if current.lower() == original_status.lower():
            print(f"  [OK] Restored to {original_status}")
        else:
            print(f"  [WARN] Ended at {current}, not {original_status}")

    @staticmethod
    def _print_transitions(transitions):
        print("  | ID | Name | To |")
        print("  |----|------|----|")
        for t in transitions:
            print(f"  | {t['id']} | {t['name']} | {t['to']['name']} |")
        print()


SKILL_DIR = __import__("os").path.dirname(
    __import__("os").path.dirname(__import__("os").path.abspath(__file__))
)


def load_config(project_key):
    path = f"{SKILL_DIR}/{project_key}.config"
    import os as _os

    if not _os.path.exists(path):
        return None
    config = {"milestones": {}, "transitions": {}}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k.upper() == "PIPELINE":
                continue
            if "=" in v:
                transitions = {}
                for pair in v.split(","):
                    parts = pair.split("=", 1)
                    if len(parts) == 2:
                        transitions[parts[0].strip()] = parts[1].strip()
                if transitions:
                    config["transitions"][k] = transitions
            else:
                config["milestones"][k] = [s.strip() for s in v.split(",") if s.strip()]
    return config


def save_config(project_key, config, pipeline_order=None):
    path = f"{SKILL_DIR}/{project_key}.config"
    import os as _os

    lines = [f"# Jira Move - {project_key} Transitions", ""]
    if config.get("milestones"):
        ordered = pipeline_order or sorted(config["milestones"].keys())
        for ms in ordered:
            if ms in config["milestones"]:
                lines.append(f"{ms}={', '.join(config['milestones'][ms])}")
        lines.append("")
    for status_name, transitions in sorted(config["transitions"].items()):
        if not transitions:
            continue
        pairs = [f"{tid}={to_name}" for tid, to_name in sorted(transitions.items())]
        lines.append(f"{status_name}={','.join(pairs)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
