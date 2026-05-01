from typing import Protocol, List
from .machine_state import MachineState
from .command_model import MoveCommand, ArcCommand
from .motion_segments import LinearSegment, ArcSegment


class LinearPlannerInterface(Protocol):
    def plan(self, cmd: MoveCommand, state: MachineState) -> List[LinearSegment]:
        ...


class ArcPlannerInterface(Protocol):
    def plan(self, cmd: ArcCommand, state: MachineState) -> List[ArcSegment]:
        ...
