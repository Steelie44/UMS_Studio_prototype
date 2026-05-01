from typing import Iterable

from ..command_model import (
    ArcCommand,
    CoolantCommand,
    DwellCommand,
    MoveCommand,
    SpindleCommand,
)
from ..errors import ValidatorError
from .targets import TargetProfile, get_target


class GCodeEmitter:
    def __init__(self, target: str | TargetProfile):
        self.target = get_target(target) if isinstance(target, str) else target

    def emit(self, commands: Iterable[object]) -> str:
        lines: list[str] = list(self.target.header)
        for command in commands:
            lines.extend(self._emit_command(command))
        for footer_line in self.target.footer:
            if not lines or lines[-1] != footer_line:
                lines.append(footer_line)
        return "\n".join(lines) + "\n"

    def _emit_command(self, command: object) -> list[str]:
        if isinstance(command, MoveCommand):
            return [self._emit_move(command)]
        if isinstance(command, ArcCommand):
            return [self._emit_arc(command)]
        if isinstance(command, DwellCommand):
            return [self._emit_dwell(command)]
        if isinstance(command, SpindleCommand):
            return [self._emit_spindle(command)]
        if isinstance(command, CoolantCommand):
            return self._emit_coolant(command)
        raise ValidatorError(f"Cannot emit unsupported command {type(command)}")

    def _emit_move(self, command: MoveCommand) -> str:
        parts = ["G0" if command.rapid else "G1"]
        parts.extend(self._format_words(command.axes))
        if command.feed_rate is not None and not command.rapid:
            parts.append(self._format_number("F", command.feed_rate))
        return " ".join(parts)

    def _emit_arc(self, command: ArcCommand) -> str:
        parts = ["G2" if command.clockwise else "G3"]
        parts.extend(self._format_words(command.axes))
        parts.extend(self._format_words(command.center_offset))
        if command.feed_rate is not None:
            parts.append(self._format_number("F", command.feed_rate))
        return " ".join(parts)

    def _emit_dwell(self, command: DwellCommand) -> str:
        if self.target.dwell_uses_milliseconds:
            return f"G4 {self._format_number('P', command.duration_ms)}"
        seconds = command.duration_ms / 1000
        return f"G4 {self._format_number('P', seconds)}"

    def _emit_spindle(self, command: SpindleCommand) -> str:
        if not command.enabled:
            return "M5"
        if command.direction == "CCW" and not self.target.supports_spindle_ccw:
            raise ValidatorError(f"{self.target.name} target does not support CCW spindle output")
        code = "M4" if command.direction == "CCW" else "M3"
        if command.speed is None:
            return code
        return f"{code} {self._format_number('S', command.speed)}"

    def _emit_coolant(self, command: CoolantCommand) -> list[str]:
        if command.flood:
            return [self.target.flood_coolant_on]
        if command.mist:
            if not self.target.supports_mist_coolant:
                raise ValidatorError(f"{self.target.name} target does not support mist coolant")
            return ["M7"]
        return [self.target.coolant_off]

    def _format_words(self, words: dict[str, float]) -> list[str]:
        return [self._format_number(key, value) for key, value in words.items()]

    def _format_number(self, letter: str, value: float | int) -> str:
        if isinstance(value, int) or float(value).is_integer():
            return f"{letter}{int(value)}"
        return f"{letter}{value:.4f}".rstrip("0").rstrip(".")
