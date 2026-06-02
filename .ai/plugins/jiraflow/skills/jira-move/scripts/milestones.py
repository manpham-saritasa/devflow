"""Milestones — load and resolve milestone names to project statuses."""

import os

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Milestones:
    def __init__(self):
        self.milestones = {}  # milestone → [status names]
        self.pipeline = []  # ordered milestone names
        self._load()

    def _load(self):
        path = os.path.join(SKILL_DIR, "milestones.config")
        if not os.path.exists(path):
            return
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k.upper() == "PIPELINE":
                    self.pipeline = [s.strip() for s in v.split(",") if s.strip()]
                else:
                    self.milestones[k] = [s.strip() for s in v.split(",") if s.strip()]

    def resolve(self, target, project_transitions=None):
        tl = target.lower().replace("-", " ")
        # Check milestone keys (normalized from hyphens)
        for mname, statuses in self.milestones.items():
            if mname.replace("-", " ") == tl:
                candidates = statuses
                if project_transitions:
                    for s in candidates:
                        if s in project_transitions or any(
                            s.lower() == t.lower() for t in project_transitions
                        ):
                            return s
                return candidates[0]
        # Check status names directly
        for statuses in self.milestones.values():
            for s in statuses:
                if s.lower() == tl:
                    return s
        return target

    def status_to_milestone(self, status_name):
        """Find which milestone a Jira status belongs to."""
        sl = status_name.lower()
        for mname, statuses in self.milestones.items():
            for s in statuses:
                if s.lower() == sl:
                    return mname
        for mname, statuses in self.milestones.items():
            for s in statuses:
                if s.lower() in sl or sl in s.lower():
                    return mname
        return None

    def next(self, current_milestone):
        """Return next milestone in pipeline, or None if at end."""
        try:
            idx = self.pipeline.index(current_milestone)
            if idx + 1 < len(self.pipeline):
                return self.pipeline[idx + 1]
        except ValueError:
            pass
        return None

    def is_last(self, milestone):
        if not self.pipeline:
            return False
        return milestone == self.pipeline[-1]
