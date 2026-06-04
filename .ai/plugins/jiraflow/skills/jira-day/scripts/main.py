"""Find Jira tasks touched in the last N hours and suggest the best candidate."""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from auth import (
    detect_identity,
    load_env,
    persist_identity_if_changed,
    validate_project_key,
)
from collectors import collect_candidates
from common import ROLES, find_repo_root
from context import RuntimeContext
from output import build_output, rank_candidates
from settings import (
    ensure_local_config,
    load_stage_groups,
    merge_stage_groups,
)

ROOT = find_repo_root(__file__)
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DIR = os.path.join(ROOT, ".local", "jday")
CONFIG_PATH = os.path.join(LOCAL_DIR, "config.yaml")
CONFIG_TEMPLATE_PATH = os.path.join(SKILL_DIR, "config.template.yaml")


def parse_args(argv: list[str]) -> dict[str, object]:
    args: dict[str, object] = {
        "project": None,
        "json": False,
        "config": False,
        "reset_role": False,
        "role": None,
        "window": 24,
        "no_pr": False,
    }
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--json":
            args["json"] = True
        elif arg == "--config":
            args["config"] = True
        elif arg == "--reset-role":
            args["reset_role"] = True
        elif arg == "--no-pr":
            args["no_pr"] = True
        elif arg == "--role" and i + 1 < len(argv):
            args["role"] = argv[i + 1].lower()
            i += 1
        elif arg == "--window" and i + 1 < len(argv):
            window = argv[i + 1].lower()
            args["window"] = int(window[:-1]) if window.endswith("h") else int(window)
            if int(args["window"]) <= 0:
                raise SystemExit("--window must be a positive number of hours")
            i += 1
        elif not arg.startswith("--") and args["project"] is None:
            args["project"] = arg.upper()
        i += 1
    return args


def resolve_runtime(
    args: dict[str, object],
) -> tuple[dict[str, str], dict, RuntimeContext]:
    config = ensure_local_config(
        CONFIG_PATH, CONFIG_TEMPLATE_PATH, LOCAL_DIR, bool(args["reset_role"])
    )
    env = load_env(ROOT)
    identity = detect_identity(config, env, ROOT)
    persist_identity_if_changed(config, identity, CONFIG_PATH, LOCAL_DIR)

    role = str(args["role"] or config.get("role") or "mixed")
    if role not in ROLES:
        role = "mixed"
    project = str(args["project"] or env.get("JIRA_PROJECT_KEY", "PROJ"))
    validate_project_key(project)
    check_pr = bool(config.get("check_pr_activity", False)) and not bool(args["no_pr"])
    stage_groups = merge_stage_groups(
        load_stage_groups(ROOT), config.get("stage_groups")
    )
    runtime = RuntimeContext(
        project=project,
        role=role,
        check_pr=check_pr,
        stage_groups=stage_groups,
        window_hours=int(args["window"]),
        jira_domain=env.get("JIRA_COMPANY_DOMAIN", ""),
        prefer_projects=config.get("prefer_projects") or [],
    )
    return env, config, runtime


def config_output(
    config: dict,
    runtime: RuntimeContext,
) -> str:
    return json.dumps(
        {
            "project": runtime.project,
            "role": runtime.role,
            "check_pr_activity": runtime.check_pr,
            "identity": config.get("identity") or {},
            "config_path": CONFIG_PATH,
            "stage_groups": runtime.stage_groups,
            "jira_domain": runtime.jira_domain,
        },
        indent=2,
    )


def json_output(
    ranked,
    runtime: RuntimeContext,
) -> str:
    return json.dumps(
        {
            "project": runtime.project,
            "window_hours": runtime.window_hours,
            "role": runtime.role,
            "check_pr_activity": runtime.check_pr,
            "suggested_index": 1 if ranked else None,
            "items": [x.to_dict(runtime) for x in ranked],
        },
        indent=2,
    )


def main() -> None:
    args = parse_args(sys.argv)
    env, config, runtime = resolve_runtime(args)

    if bool(args["config"]):
        print(config_output(config, runtime))
        return

    candidates = collect_candidates(ROOT, env, config, runtime)
    ranked = rank_candidates(candidates, runtime)

    if bool(args["json"]):
        print(json_output(ranked, runtime))
        return

    print(build_output(ranked, runtime))


if __name__ == "__main__":
    main()
