from dataclasses import dataclass
import math
from typing import Iterable

from ..command_model import ArcCommand, MoveCommand


@dataclass(frozen=True)
class PreviewSegment:
    kind: str
    points: tuple[tuple[float, float], ...]


def build_preview_segments(commands: Iterable[object]) -> list[PreviewSegment]:
    x = 0.0
    y = 0.0
    segments: list[PreviewSegment] = []

    for command in commands:
        if isinstance(command, MoveCommand):
            next_x = command.axes.get("X", x)
            next_y = command.axes.get("Y", y)
            if (next_x, next_y) != (x, y):
                kind = "rapid" if command.rapid else "feed"
                segments.append(PreviewSegment(kind, ((x, y), (next_x, next_y))))
            x, y = next_x, next_y
        elif isinstance(command, ArcCommand):
            next_x = command.axes.get("X", x)
            next_y = command.axes.get("Y", y)
            center_x = x + command.center_offset.get("I", 0.0)
            center_y = y + command.center_offset.get("J", 0.0)
            points = _arc_points(x, y, next_x, next_y, center_x, center_y, command.clockwise)
            if len(points) > 1:
                segments.append(PreviewSegment("arc", tuple(points)))
            x, y = next_x, next_y

    return segments


def _arc_points(start_x, start_y, end_x, end_y, center_x, center_y, clockwise):
    radius = math.hypot(start_x - center_x, start_y - center_y)
    if radius == 0:
        return [(start_x, start_y), (end_x, end_y)]

    start_angle = math.atan2(start_y - center_y, start_x - center_x)
    end_angle = math.atan2(end_y - center_y, end_x - center_x)

    if clockwise and end_angle >= start_angle:
        end_angle -= math.tau
    elif not clockwise and end_angle <= start_angle:
        end_angle += math.tau

    steps = max(8, int(abs(end_angle - start_angle) / math.tau * 48))
    points = []
    for step in range(steps + 1):
        t = step / steps
        angle = start_angle + (end_angle - start_angle) * t
        points.append((center_x + math.cos(angle) * radius, center_y + math.sin(angle) * radius))
    return points
