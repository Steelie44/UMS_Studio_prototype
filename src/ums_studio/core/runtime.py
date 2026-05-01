from typing import List, Any
from .machine_state import MachineState
from .command_model import (
    MoveCommand,
    ArcCommand,
    DwellCommand,
    SpindleCommand,
    CoolantCommand,
)
from .motion_segments import (
    LinearSegment,
    ArcSegment,
    DwellSegment,
    SpindleSegment,
    CoolantSegment,
)
from .machine_session import MachineSession
from ..planner.planner_registry import PlannerRegistry


class Runtime:
    def __init__(self, session: MachineSession, planners: PlannerRegistry):
        self.session = session
        self.planners = planners
        self.state = MachineState()
      

    def plan(self, commands: List[Any]) -> List[Any]:
        segments: List[Any] = []
        for cmd in commands:
            if isinstance(cmd, MoveCommand):
                planner = self.planners.get_linear()
                segments.extend(planner.plan(cmd, self.state))
            elif isinstance(cmd, ArcCommand):
                planner = self.planners.get_arc()
                segments.extend(planner.plan(cmd, self.state))
            elif isinstance(cmd, DwellCommand):
                segments.append(DwellSegment(duration_ms=cmd.duration_ms))
            elif isinstance(cmd, SpindleCommand):
                segments.append(
                    SpindleSegment(
                        enabled=cmd.enabled,
                        speed=cmd.speed,
                        direction=cmd.direction,
                    )
                )
            elif isinstance(cmd, CoolantCommand):
                segments.append(
                    CoolantSegment(
                        flood=cmd.flood,
                        mist=cmd.mist,
                    )
                )
        return segments
