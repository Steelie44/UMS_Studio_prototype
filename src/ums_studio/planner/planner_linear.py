from typing import List
import math
from ..core.motion_segments import LinearSegment
from ..core.command_model import MoveCommand
from ..core.machine_state import MachineState


class LinearPlanner:
    def __init__(self, segment_length_mm: float = 1.0):
        self.segment_length_mm = segment_length_mm

    def plan(self, cmd: MoveCommand, state: MachineState) -> List[LinearSegment]:
        start = {a: s.position for a, s in state.axes.items()}
        target = start.copy()
        for axis, value in cmd.axes.items():
            target[axis] = value
        dx2 = 0.0
        for axis in target.keys():
            dx = target[axis] - start[axis]
            dx2 += dx * dx
        distance = math.sqrt(dx2)
        if distance == 0:
            return [LinearSegment(target=target, feed_rate=cmd.feed_rate or state.feed_rate, rapid=cmd.rapid)]
        steps = max(1, int(math.ceil(distance / self.segment_length_mm)))
        segments: List[LinearSegment] = []
        for i in range(1, steps + 1):
            t = i / steps
            seg_target = {axis: start[axis] + (target[axis] - start[axis]) * t for axis in target.keys()}
            segments.append(LinearSegment(target=seg_target, feed_rate=cmd.feed_rate or state.feed_rate, rapid=cmd.rapid))
        return segments
