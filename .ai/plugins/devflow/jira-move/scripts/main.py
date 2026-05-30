"""Transition a Jira issue through dev pipeline. Usage: python main.py KEY [MILESTONE] [--discover]"""

import base64
import os
import sys

from discover import Discoverer, load_config
from milestones import Milestones
from mover import Mover
from pipeline import Pipeline

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


def main():
    env = load_env()
    domain = env["JIRA_COMPANY_DOMAIN"]
    email = env["JIRA_EMAIL"]
    token = env["JIRA_API_TOKEN"]
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()

    milestones = Milestones()
    pipeline = Pipeline(milestones)

    if len(sys.argv) < 2:
        ms_list = (
            ", ".join(milestones.pipeline)
            if milestones.pipeline
            else "ready, review, qa"
        )
        print(f"Usage: python main.py KEY [{ms_list}] [--discover]")
        return

    key = sys.argv[1].upper()

    if "--discover" in sys.argv:
        Discoverer(domain, auth, milestones, pipeline).run(key)
        return

    project_key = key.split("-")[0]
    config = load_config(project_key)
    if not config or not config["transitions"]:
        print(f"❌ No config for {project_key}. Run --discover first.")
        return

    mover = Mover(domain, auth, config, milestones, pipeline)

    if len(sys.argv) >= 3:
        mover.move(key, sys.argv[2])
    else:
        mover.auto_advance(key)


if __name__ == "__main__":
    main()
