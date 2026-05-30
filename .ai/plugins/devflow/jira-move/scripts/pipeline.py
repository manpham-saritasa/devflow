"""Pipeline — navigate milestone order for routing between milestones."""


class Pipeline:
    def __init__(self, milestones):
        self.order = list(milestones.pipeline)

    def path_to(self, from_milestone, to_milestone):
        """Return list of milestones from after 'from' through 'to' (inclusive)."""
        try:
            start = self.order.index(from_milestone)
            end = self.order.index(to_milestone)
            if end > start:
                return self.order[start + 1 : end + 1]
        except ValueError:
            pass
        return []

    def position(self, milestone):
        try:
            return self.order.index(milestone)
        except ValueError:
            return -1

    def is_ahead(self, from_milestone, to_milestone):
        """Is 'to' after 'from' in the pipeline?"""
        return self.position(to_milestone) > self.position(from_milestone)

    def is_last(self, milestone):
        if not self.order:
            return False
        return milestone == self.order[-1]
