from .planner_linear import LinearPlanner
from .planner_arc import ArcPlanner


class PlannerRegistry:
    def __init__(self):
        self._linear = LinearPlanner()
        self._arc = ArcPlanner()

    def get_linear(self) -> LinearPlanner:
        return self._linear

    def get_arc(self) -> ArcPlanner:
        return self._arc
