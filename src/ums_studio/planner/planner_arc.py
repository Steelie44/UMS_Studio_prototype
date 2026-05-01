from typing import List
import math
from ..core.motion_segments import ArcSegment
from ..core.command_model import ArcCommand
from ..core.machine_state import MachineState


class ArcPlanner:
    def __init__(self, max_angle_deg: float = 5.0):
        self.max_angle_rad = math.radians(max_angle_deg)

    def plan(self, cmd: ArcCommand, state: MachineState) -> List[ArcSegment]:
        start = {a: s.position for a, s in state.axes.items()}
        target = start.copy()
        for axis, value in cmd.axes.items():
            target[axis] = value
        cx = start["X"] + cmd.center_offset.get("I", 0.0)
        cy = start["Y"] + cmd.center_offset.get("J", 0.0)
        sx = start["X"] - cx
        sy = start["Y"] - cy
        ex = target["X"] - cx
        ey = target["Y"] - cy
        r_start = math.atan2(sy, sx)
        r_end = math.atan2(ey, ex)
        if cmd.clockwise:
            if r_end >= r_start:
                r_end -= 2 * math.pi
        else:
            if r_end <= r_start:
                r_end += 2 * math.pi
        total_angle = r_end - r_start
        steps = max(1, int(math.ceil(abs(total_angle) / self.max_angle_rad)))
        angle_step = total_angle / steps
        segments: List[ArcSegment] = []
        radius = math.hypot(sx, sy)
        for i in range(1, steps + 1):
            a = r_start + angle_step * i
            x = cx + math.cos(a) * radius
            y = cy + math.sin(a) * radius
            seg_target = target.copy()
            seg_target["X"] = x
            seg_target["Y"] = y
            segments.append(ArcSegment(target=seg_target, center_offset=cmd.center_offset, clockwise=cmd.clockwise, feed_rate=cmd.feed_rate or state.feed_rate))
        return segments
