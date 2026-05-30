"""Transition a Jira issue through dev pipeline. Usage: python main.py KEY [MILESTONE] [--discover]"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SKILL_DIR))))


def load_env():
    env = {}
    for fname in [".env.local", ".env"]:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"')
    return env


def load_milestones():
    path = os.path.join(SKILL_DIR, "milestones.config")
    if not os.path.exists(path):
        return {}, []
    milestones = {}
    pipeline = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k.upper() == "PIPELINE":
                pipeline = [s.strip() for s in v.split(",") if s.strip()]
            else:
                milestones[k] = [s.strip() for s in v.split(",") if s.strip()]
    return milestones, pipeline


def status_to_milestone(status_name, milestones):
    sl = status_name.lower()
    for mname, statuses in milestones.items():
        for s in statuses:
            if s.lower() == sl:
                return mname
    for mname, statuses in milestones.items():
        for s in statuses:
            if s.lower() in sl or sl in s.lower():
                return mname
    return None


def resolve_target(
    target, milestones, project_milestones=None, project_transitions=None
):
    """Resolve milestone/status name to actual Jira status.
    Checks project config first, then global milestones.config.
    If project_transitions provided, picks the first status that exists in the project."""
    tl = target.lower()
    # Check project config first (cached from --discover)
    if project_milestones:
        if tl in project_milestones:
            for s in project_milestones[tl]:
                return s
        for mname, statuses in project_milestones.items():
            for s in statuses:
                if s.lower() == tl:
                    return s
    # Fall back to global milestones
    if tl in milestones:
        candidates = milestones[tl]
        if project_transitions:
            # Pick first candidate that exists in this project
            for s in candidates:
                if s in project_transitions or any(
                    s.lower() == t.lower() for t in project_transitions
                ):
                    return s
        return candidates[0]
    for mname, statuses in milestones.items():
        for s in statuses:
            if s.lower() == tl:
                return s
    return target


def load_config(project_key):
    path = os.path.join(SKILL_DIR, f"{project_key}.config")
    if not os.path.exists(path):
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
                # Transition map: STATUS=ID=TO,ID=TO
                transitions = {}
                for pair in v.split(","):
                    parts = pair.split("=", 1)
                    if len(parts) == 2:
                        transitions[parts[0].strip()] = parts[1].strip()
                if transitions:
                    config["transitions"][k] = transitions
            else:
                # Milestone mapping: milestone=Status1,Status2
                config["milestones"][k] = [s.strip() for s in v.split(",") if s.strip()]
    return config


def save_config(project_key, config):
    path = os.path.join(SKILL_DIR, f"{project_key}.config")
    lines = [
        f"# Jira Move — {project_key} Transitions",
        "",
    ]
    # Milestone mappings first
    if config.get("milestones"):
        for ms, statuses in sorted(config["milestones"].items()):
            lines.append(f"{ms}={', '.join(statuses)}")
        lines.append("")
    # Transition map
    for status_name, transitions in sorted(config["transitions"].items()):
        if not transitions:
            continue
        pairs = [f"{tid}={to_name}" for tid, to_name in sorted(transitions.items())]
        lines.append(f"{status_name}={','.join(pairs)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def jira_get(domain, auth, path):
    req = urllib.request.Request(f"https://{domain}.atlassian.net/rest/api/3{path}")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_status(domain, auth, key):
    return jira_get(domain, auth, f"/issue/{key}?fields=status")["fields"]["status"][
        "name"
    ]


def get_transitions(domain, auth, key):
    return jira_get(domain, auth, f"/issue/{key}/transitions")["transitions"]


def execute_transition(domain, auth, key, transition_id):
    body = json.dumps({"transition": {"id": transition_id}}).encode()
    req = urllib.request.Request(
        f"https://{domain}.atlassian.net/rest/api/3/issue/{key}/transitions", data=body
    )
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()) if resp.status != 204 else {}
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


def get_all_statuses(domain, auth, project_key):
    statuses = set()
    try:
        data = jira_get(domain, auth, f"/project/{project_key}/statuses")
        for issue_type in data:
            for status in issue_type.get("statuses", []):
                statuses.add(status["name"])
    except Exception:
        pass
    return sorted(statuses)


def discover(domain, auth, key, milestones, pipeline):
    project_key = key.split("-")[0]
    config = load_config(project_key) or {"milestones": {}, "transitions": {}}
    original_status = get_status(domain, auth, key)

    print(f"## Discovering workflow for {project_key} using {key}\n")
    print(f"Original status: {original_status}\n")

    all_statuses = get_all_statuses(domain, auth, project_key)
    if all_statuses:
        print(f"### Project Statuses ({len(all_statuses)}):")
        for s in all_statuses:
            ms = status_to_milestone(s, milestones) or "—"
            print(f"  - {s}  [{ms}]")
        print()

    visited = set()
    discovered_milestones = {}  # milestone → [status names found in this project]
    stage = 0

    for milestone_name in pipeline:
        stage += 1
        current = get_status(domain, auth, key)
        current_milestone = status_to_milestone(current, milestones) or current
        print(
            f"### Stage {stage}: Milestone '{milestone_name}' (current: {current} [{current_milestone}])"
        )

        # Record transitions from current state
        if current not in visited:
            transitions = get_transitions(domain, auth, key)
            config["transitions"][current] = {
                str(t["id"]): t["to"]["name"] for t in transitions
            }
            visited.add(current)
            # Map current status to its milestone
            current_ms = status_to_milestone(current, milestones)
            if current_ms:
                discovered_milestones.setdefault(current_ms, [])
                if current not in discovered_milestones[current_ms]:
                    discovered_milestones[current_ms].append(current)
            print_transitions(transitions)

        if current_milestone == milestone_name:
            print(f"  ✅ Already at milestone '{milestone_name}'\n")
            continue

        if stage == len(pipeline):
            continue

        trans_map = config["transitions"].get(current, {})
        tid = None
        for id_candidate, to_name in trans_map.items():
            to_milestone = status_to_milestone(to_name, milestones)
            if to_milestone == milestone_name:
                tid = id_candidate
                break

        if tid:
            try:
                execute_transition(domain, auth, key, tid)
                new = get_status(domain, auth, key)
                print(f"  ✅ Moved to {new}\n")
            except RuntimeError as e:
                print(f"  🛑 Can't move: {e}")
                print(
                    f"  → Move '{key}' to milestone '{milestone_name}' manually, then re-run --discover."
                )
                save_config(project_key, config)
                return
        else:
            print(
                f"  ❌ No transition to milestone '{milestone_name}' from '{current}'"
            )
            print(f"  → Move '{key}' manually, then re-run --discover.")
            save_config(project_key, config)
            return

    current = get_status(domain, auth, key)
    if current not in visited:
        transitions = get_transitions(domain, auth, key)
        config["transitions"][current] = {
            str(t["id"]): t["to"]["name"] for t in transitions
        }
        visited.add(current)

    config["milestones"] = discovered_milestones
    save_config(project_key, config)

    total_transitions = sum(len(t) for t in config["transitions"].values())
    print(f"\n### Summary — {len(visited)} states, {total_transitions} transitions")
    for status_name in sorted(visited):
        ms = status_to_milestone(status_name, milestones) or "—"
        trans_map = config["transitions"].get(status_name, {})
        if trans_map:
            to_list = ", ".join(trans_map.values())
            print(f"  {status_name}  [{ms}] → {to_list}")

    current = get_status(domain, auth, key)
    if current.lower() != original_status.lower():
        print(f"\n↩️  Restoring {key} to {original_status}...")
        restore_task(domain, auth, key, config, original_status)


def restore_task(domain, auth, key, config, original_status):
    current = get_status(domain, auth, key)
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
            print(f"  ⚠️ No reverse path from {current}")
            break
        execute_transition(domain, auth, key, tid)
        current = get_status(domain, auth, key)
        print(f"  → {current}")
    if current.lower() == original_status.lower():
        print(f"  ✅ Restored to {original_status}")
    else:
        print(f"  ⚠️ Ended at {current}, not {original_status}")


def print_transitions(transitions):
    print("  | ID | Name | To |")
    print("  |----|------|----|")
    for t in transitions:
        print(f"  | {t['id']} | {t['name']} | {t['to']['name']} |")
    print()


def move(domain, auth, key, target, milestones, pipeline=None):
    project_key = key.split("-")[0]
    config = load_config(project_key)
    if not config or not config["transitions"]:
        print(f"❌ No config for {project_key}. Run --discover first.")
        return

    # Build pipeline order from milestones
    if pipeline is None:
        pipeline = list(milestones.keys())

    target_name = resolve_target(
        target, milestones, config.get("milestones"), list(config["transitions"].keys())
    )
    current = get_status(domain, auth, key)
    print(f"Current: {current} → Target: {target_name}")

    if current.lower() == target_name.lower():
        print(f"✅ Already at {target_name}")
        return

    trans_map = config["transitions"].get(current, {})
    tid = None
    for id_candidate, to_name in trans_map.items():
        if to_name.lower() == target_name.lower():
            tid = id_candidate
            break

    if not tid:
        transitions = get_transitions(domain, auth, key)
        config["transitions"][current] = {
            str(t["id"]): t["to"]["name"] for t in transitions
        }
        trans_map = config["transitions"][current]
        for id_candidate, to_name in trans_map.items():
            if to_name.lower() == target_name.lower():
                tid = id_candidate
                break

    if not tid:
        # Smart routing: walk pipeline to reach target milestone
        current_ms = status_to_milestone(current, milestones)
        target_ms = status_to_milestone(target_name, milestones) or target.lower()

        if current_ms and target_ms and pipeline:
            try:
                current_idx = pipeline.index(current_ms)
                target_idx = pipeline.index(target_ms)
                if target_idx > current_idx:
                    print(
                        f"  → Routing through pipeline: {current_ms} → ... → {target_ms}"
                    )
                    for step_ms in pipeline[current_idx + 1 : target_idx + 1]:
                        step_target = resolve_target(
                            step_ms,
                            milestones,
                            config.get("milestones"),
                            list(config["transitions"].keys()),
                        )
                        step_tid = None
                        step_trans = config["transitions"].get(
                            get_status(domain, auth, key), {}
                        )
                        for id_candidate, to_name in step_trans.items():
                            if to_name.lower() == step_target.lower():
                                step_tid = id_candidate
                                break
                        if not step_tid:
                            print(
                                f"  ⚠️  Stuck at {get_status(domain, auth, key)} — can't reach {step_ms}"
                            )
                            return
                        try:
                            execute_transition(domain, auth, key, step_tid)
                            new = get_status(domain, auth, key)
                            print(f"  → {new}")
                        except RuntimeError as e:
                            print(f"  ⚠️  Failed at {step_ms}: {e}")
                            return
                    final = get_status(domain, auth, key)
                    print(f"✅ {key} → {final}")
                    return
            except ValueError:
                pass

        # Fallback for backlog: move to ready first, then backlog
        is_backlog = target.lower() == "backlog" or (
            target.lower() in milestones and target.lower() == "backlog"
        )
        if is_backlog:
            print(f"  → No direct path to backlog, trying via ready...")
            ready_target = resolve_target(
                "ready",
                milestones,
                config.get("milestones"),
                list(config["transitions"].keys()),
            )
            ready_tid = None
            for id_candidate, to_name in trans_map.items():
                if to_name.lower() == ready_target.lower():
                    ready_tid = id_candidate
                    break
            if ready_tid:
                try:
                    execute_transition(domain, auth, key, ready_tid)
                    ready_status = get_status(domain, auth, key)
                    print(f"  → {ready_status}")
                    ready_trans = config["transitions"].get(ready_status, {})
                    for id_candidate, to_name in ready_trans.items():
                        if (
                            to_name.lower() == "backlog"
                            or status_to_milestone(to_name, milestones) == "backlog"
                        ):
                            try:
                                execute_transition(domain, auth, key, id_candidate)
                                final = get_status(domain, auth, key)
                                print(f"✅ {key} → {final}")
                            except RuntimeError as e:
                                print(
                                    f"⚠️  Moved to {ready_status} but couldn't reach backlog: {e}"
                                )
                            return
                    print(
                        f"⚠️  Moved to {ready_status} but no transition to backlog from there."
                    )
                except RuntimeError as e:
                    print(f"⚠️  Failed to move to {ready_target}: {e}")
                return

        print(f"⚠️  No transition from {current} to {target_name}.")
        return

    try:
        execute_transition(domain, auth, key, tid)
        new = get_status(domain, auth, key)
        print(f"✅ {key} → {new}")
    except RuntimeError as e:
        print(f"⚠️  Failed: {e}")


def auto_move(domain, auth, key, milestones, pipeline):
    current = get_status(domain, auth, key)
    cm = status_to_milestone(current, milestones)
    if cm is None:
        print(
            f"⚠️  Current status '{current}' not in milestones. Use milestone name directly."
        )
        return
    try:
        idx = pipeline.index(cm)
    except ValueError:
        print(f"⚠️  Milestone '{cm}' not in pipeline.")
        return
    if idx + 1 >= len(pipeline):
        print(f"✅ Dev pipeline complete for {key}.")
        return
    next_ms = pipeline[idx + 1]
    print(f"Auto: {current} ({cm}) → {next_ms}")
    move(domain, auth, key, next_ms, milestones)


def main():
    env = load_env()
    domain = env["JIRA_COMPANY_DOMAIN"]
    email = env["JIRA_EMAIL"]
    token = env["JIRA_API_TOKEN"]
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    milestones, pipeline = load_milestones()

    if len(sys.argv) < 2:
        ms_list = ", ".join(pipeline) if pipeline else "ready, review, qa"
        print(f"Usage: python main.py KEY [{ms_list}] [--discover]")
        return

    key = sys.argv[1].upper()
    is_discover = "--discover" in sys.argv

    if is_discover:
        discover(domain, auth, key, milestones, pipeline)
        return

    if len(sys.argv) >= 3:
        move(domain, auth, key, sys.argv[2], milestones, pipeline)
    else:
        auto_move(domain, auth, key, milestones, pipeline)


if __name__ == "__main__":
    main()
