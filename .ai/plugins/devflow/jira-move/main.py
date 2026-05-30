"""Transition a Jira issue through dev pipeline. Usage: python main.py KEY [MILESTONE] [--discover]"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SKILL_DIR))))

MILESTONE_ALIASES = {
    "ready": "Ready for Development",
    "in-progress": "In Progress",
    "review": "Code Review",
    "qa": "Ready for QA",
}

AUTO_NEXT = {
    "backlog": "ready",
    "ready for development": "in-progress",
    "in progress": "review",
    "code review": "qa",
    "ready for qa": "done",
}


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


def load_config(project_key):
    path = os.path.join(SKILL_DIR, f"{project_key}.config")
    if not os.path.exists(path):
        return None
    config = {"pipeline": [], "transitions": {}}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k == "PIPELINE":
                config["pipeline"] = [s.strip() for s in v.split(",") if s.strip()]
            elif "," in v and "=" in v:
                # Transition map: STATUS=ID=TO,ID=TO
                transitions = {}
                for pair in v.split(","):
                    parts = pair.split("=", 1)
                    if len(parts) == 2:
                        transitions[parts[0].strip()] = parts[1].strip()
                config["transitions"][k] = transitions
    return config


def save_config(project_key, config):
    path = os.path.join(SKILL_DIR, f"{project_key}.config")
    lines = [
        f"# Jira Move — {project_key} Transitions",
        "",
        f"PIPELINE={', '.join(config['pipeline'])}",
        "",
    ]
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


def jira_post(domain, auth, path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"https://{domain}.atlassian.net/rest/api/3{path}", data=data
    )
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def discover(domain, auth, key):
    project_key = key.split("-")[0]
    config = load_config(project_key) or {"pipeline": [], "transitions": {}}
    original_status = get_status(domain, auth, key)

    print(f"## Discovering workflow for {project_key} using {key}\n")
    print(f"Original status: {original_status}\n")

    all_statuses = get_all_statuses(domain, auth, project_key)
    if all_statuses:
        print(f"### Project Statuses ({len(all_statuses)}):")
        for s in all_statuses:
            print(f"  - {s}")
        print()

    # Build pipeline from known dev statuses + visited states
    visited = set()
    pipeline = list(config["pipeline"])
    stage = 0

    for target_name in pipeline:
        stage += 1
        current = get_status(domain, auth, key)
        print(f"### Stage {stage}: Looking for '{target_name}' (current: {current})")

        # Record transitions from current state
        if current not in visited:
            transitions = get_transitions(domain, auth, key)
            config["transitions"][current] = {
                str(t["id"]): t["to"]["name"] for t in transitions
            }
            visited.add(current)
            print_transitions(transitions)

        if current.lower() == target_name.lower():
            continue

        # Skip move if target is the last pipeline stage (already discovered from current)
        if stage == len(pipeline):
            continue

        # Try to move
        trans_map = config["transitions"].get(current, {})
        tid = None
        for id_candidate, to_name in trans_map.items():
            if to_name.lower() == target_name.lower():
                tid = id_candidate
                break

        if tid:
            try:
                execute_transition(domain, auth, key, tid)
                new = get_status(domain, auth, key)
                print(f"  ✅ Moved to {new}")
            except RuntimeError as e:
                print(f"  🛑 Can't move: {e}")
                print(
                    f"  → Move '{key}' to '{target_name}' manually, then re-run --discover."
                )
                save_config(project_key, config)
                return
        else:
            print(f"  ❌ No transition to '{target_name}' from '{current}'")
            print(f"  → Move '{key}' manually, then re-run --discover.")
            save_config(project_key, config)
            return

    # Record final state
    current = get_status(domain, auth, key)
    if current not in visited:
        transitions = get_transitions(domain, auth, key)
        config["transitions"][current] = {
            str(t["id"]): t["to"]["name"] for t in transitions
        }
        visited.add(current)

    # Update pipeline with all visited states
    for s in visited:
        if s not in pipeline:
            pipeline.append(s)
    config["pipeline"] = pipeline
    save_config(project_key, config)

    total_transitions = sum(len(t) for t in config["transitions"].values())
    print(f"\n### Summary — {len(visited)} states, {total_transitions} transitions")
    for status_name in sorted(visited):
        trans_map = config["transitions"].get(status_name, {})
        if trans_map:
            to_list = ", ".join(trans_map.values())
            print(f"  {status_name} → {to_list}")

    # Restore
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

        # Direct transition to original status
        for t, name in trans_map.items():
            if name.lower() == original_status.lower():
                tid = t
                break

        # Walk backwards via Ready for Development
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


def move(domain, auth, key, milestone):
    project_key = key.split("-")[0]
    config = load_config(project_key)
    if not config or not config["pipeline"]:
        print(f"❌ No config for {project_key}. Run --discover first.")
        return

    # Resolve alias
    target_name = MILESTONE_ALIASES.get(milestone, milestone)

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
        print(f"⚠️  No transition from {current} to {target_name} in config.")
        print("   Run --discover to rebuild transition map.")
        return

    try:
        execute_transition(domain, auth, key, tid)
        new = get_status(domain, auth, key)
        print(f"✅ {key} → {new}")
    except RuntimeError as e:
        print(f"⚠️  Failed: {e}")


def auto_move(domain, auth, key):
    current = get_status(domain, auth, key).lower()
    for status_name, milestone in AUTO_NEXT.items():
        if status_name in current:
            if milestone == "done":
                print(f"✅ Dev pipeline complete for {key}. Hand off to QA.")
                return
            print(f"Auto: {current} → {milestone}")
            move(domain, auth, key, milestone)
            return
    print(f"⚠️  Current status '{current}' not in dev flow. Use ready/review/qa.")


def main():
    env = load_env()
    domain = env["JIRA_COMPANY_DOMAIN"]
    email = env["JIRA_EMAIL"]
    token = env["JIRA_API_TOKEN"]
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()

    if len(sys.argv) < 2:
        print("Usage: python main.py KEY [ready|review|qa|in-progress] [--discover]")
        return

    key = sys.argv[1].upper()
    is_discover = "--discover" in sys.argv

    if is_discover:
        discover(domain, auth, key)
        return

    if len(sys.argv) >= 3:
        move(domain, auth, key, sys.argv[2])
    else:
        auto_move(domain, auth, key)


if __name__ == "__main__":
    main()
