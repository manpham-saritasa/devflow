"""Mover - transition Jira issues between milestones or statuses."""

import json
import urllib.error
import urllib.request


class Mover:
    def __init__(self, domain, auth, config, milestones, pipeline):
        self.domain = domain
        self.auth = auth
        self.config = config
        self.milestones = milestones
        self.pipeline = pipeline

    def move(self, key, target):
        """Move task to a milestone or status name. Handles smart routing and backlog fallback."""
        target_name = self.milestones.resolve(
            target,
            list(self.config["transitions"].keys()),
        )
        current = self._get_status(key)
        print(f"Current: {current} -> Target: {target_name}")

        if current.lower() == target_name.lower():
            print(f"[OK] Already at {target_name}")
            return

        trans_map = self.config["transitions"].get(current, {})
        tid = self._find_transition(trans_map, target_name)

        if not tid:
            trans_map = self._refresh_transitions(key, current)
            tid = self._find_transition(trans_map, target_name)

        if not tid:
            self._smart_route(key, target_name, current)
            return

        self._execute(key, tid)

    def auto_advance(self, key):
        """Move to next milestone in pipeline."""
        current = self._get_status(key)
        cm = self.milestones.status_to_milestone(current)
        if cm is None:
            print(f"[WARN] Current status '{current}' not in milestones.")
            return
        next_ms = self.milestones.next(cm)
        if next_ms is None:
            print(f"[OK] Dev pipeline complete for {key}.")
            return
        print(f"Auto: {current} ({cm}) -> {next_ms}")
        self.move(key, next_ms)

    def _get_status(self, key):
        path = f"/issue/{key}?fields=status"
        data = self._jira_get(path)
        return data["fields"]["status"]["name"]

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
            new = self._get_status(key)
            print(f"[OK] {key} -> {new}")
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode())
            errors = err.get("errors", {})
            msgs = err.get("errorMessages", [])
            if isinstance(errors, dict) and errors:
                msg = f"Required: {', '.join(errors.keys())}"
            elif msgs:
                msg = "; ".join(msgs)
            else:
                msg = str(err)
            raise RuntimeError(msg) from e

    def _refresh_transitions(self, key, current):
        path = f"/issue/{key}/transitions"
        transitions = self._jira_get(path)["transitions"]
        self.config["transitions"][current] = {
            str(t["id"]): t["to"]["name"] for t in transitions
        }
        return self.config["transitions"][current]

    @staticmethod
    def _find_transition(trans_map, target_name):
        for tid, to_name in trans_map.items():
            if to_name.lower() == target_name.lower():
                return tid
        return None

    def _smart_route(self, key, target_name, current):
        current_ms = self.milestones.status_to_milestone(current)
        target_ms = (
            self.milestones.status_to_milestone(target_name) or target_name.lower()
        )

        if current_ms and target_ms and self.pipeline.is_ahead(current_ms, target_ms):
            self._route_pipeline(key, current_ms, target_ms)
            return

        if target_name.lower() == "backlog" or target_ms == "backlog":
            self._route_backlog(key, current)
            return

        print(f"[WARN] No transition from {current} to {target_name}.")

    def _fallback_to_production(self, key, step_status, step_ms, step_target, target_ms):
        """If target is complete but stuck at verify/review, try On Production first."""
        if target_ms != "complete" or step_ms not in ("verify", "review"):
            return None
        prod_target = "On Production"
        prod_trans = self.config["transitions"].get(step_status, {})
        prod_tid = self._find_transition(prod_trans, prod_target)
        if prod_tid is None:
            prod_trans = self._refresh_transitions(key, step_status)
            prod_tid = self._find_transition(prod_trans, prod_target)
        if not prod_tid:
            return None
        print(f"  -> {prod_target} (fallback)")
        self._execute_step(key, prod_tid)
        new_status = self._get_status(key)
        trans_map = self.config["transitions"].get(new_status, {})
        tid = self._find_transition(trans_map, step_target)
        if tid is None:
            trans_map_refreshed = self._refresh_transitions(key, new_status)
            tid = self._find_transition(trans_map_refreshed, step_target)
        return tid

    def _route_pipeline(self, key, current_ms, target_ms):
        path = self.pipeline.path_to(current_ms, target_ms)
        print(f"  -> Routing through pipeline: {current_ms} -> ... -> {target_ms}")
        for step_ms in path:
            step_target = self.milestones.resolve(
                step_ms, list(self.config["transitions"].keys())
            )
            step_status = self._get_status(key)
            trans_map = self.config["transitions"].get(step_status, {})
            tid = self._find_transition(trans_map, step_target)
            if tid is None:
                trans_map = self._refresh_transitions(key, step_status)
                tid = self._find_transition(trans_map, step_target)
            if tid is None:
                tid = self._fallback_to_production(key, step_status, step_ms, target_ms)
            if tid is None:
                print(f"  [WARN] Stuck at {step_status} - can't reach {step_ms}")
                return
            print(f"  -> {step_target}")
            self._execute_step(key, tid)
        new = self._get_status(key)
        print(f"[OK] {key} -> {new}")

    def _route_backlog(self, key, current):
        print("  -> No direct path to backlog, trying via ready...")
        ready_target = self.milestones.resolve(
            "ready", list(self.config["transitions"].keys())
        )
        trans_map = self.config["transitions"].get(current, {})
        ready_tid = self._find_transition(trans_map, ready_target)
        if ready_tid is None:
            trans_map = self._refresh_transitions(key, current)
            ready_tid = self._find_transition(trans_map, ready_target)
        if not ready_tid:
            return
        try:
            self._execute_step(key, ready_tid)
            ready_status = self._get_status(key)
            print(f"  -> {ready_status}")
            ready_trans = self.config["transitions"].get(ready_status, {})
            for tid, to_name in ready_trans.items():
                if (
                    to_name.lower() == "backlog"
                    or self.milestones.status_to_milestone(to_name) == "backlog"
                ):
                    self._execute_step(key, tid)
                    final = self._get_status(key)
                    print(f"[OK] {key} -> {final}")
                    return
            print(f"  [WARN] Reached {ready_status} but no transition to backlog.")
        except RuntimeError as e:
            print(f"  [WARN] Failed: {e}")

    def _execute_step(self, key, tid):
        """Execute a transition without printing final result (for multi-step)."""
        body = json.dumps({"transition": {"id": tid}}).encode()
        req = urllib.request.Request(
            f"https://{self.domain}.atlassian.net/rest/api/3/issue/{key}/transitions",
            data=body,
        )
        req.add_header("Authorization", f"Basic {self.auth}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as resp:
            if resp.status != 204:
                json.loads(resp.read())
