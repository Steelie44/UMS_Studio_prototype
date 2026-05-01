import json
from pathlib import Path
from typing import Any

from ...language.ast_nodes import ASTArc, ASTCoolant, ASTMove, ASTSpindle
from ..errors import ValidatorError


class MachineProfile:
    def __init__(self, data: dict[str, Any]):
        self.data = data
        self.name = data.get("name", "Unnamed Machine")
        self.axes = data.get("axes", {})
        self.feed = data.get("feed", {})
        self.spindle = data.get("spindle", {})
        self.capabilities = data.get("capabilities", {})

    @classmethod
    def from_file(cls, path: str | Path):
        with open(path, "r", encoding="utf-8") as f:
            return cls(json.load(f))

    def validate_ast(self, ast: list[Any]) -> list[str]:
        diagnostics: list[str] = []
        for node in ast:
            if isinstance(node, (ASTMove, ASTArc)):
                diagnostics.extend(self._validate_axes(node.axes, node.line))
                feed_rate = getattr(node, "feed_rate", None)
                if feed_rate is not None:
                    diagnostics.extend(self._validate_feed(feed_rate, node.line))
                if isinstance(node, ASTArc):
                    diagnostics.extend(self._validate_arc(node))
            elif isinstance(node, ASTSpindle):
                diagnostics.extend(self._validate_spindle(node))
            elif isinstance(node, ASTCoolant):
                diagnostics.extend(self._validate_coolant(node))
        return diagnostics

    def _validate_axes(self, axes: dict[str, float], line: int) -> list[str]:
        diagnostics = []
        for axis, value in axes.items():
            limits = self.axes.get(axis)
            if not limits:
                diagnostics.append(f"Line {line}: Axis {axis} is not supported by {self.name}.")
                continue
            axis_min = limits.get("min")
            axis_max = limits.get("max")
            if axis_min is not None and value < axis_min:
                diagnostics.append(f"Line {line}: {axis}{value:g} is below machine minimum {axis_min:g}.")
            if axis_max is not None and value > axis_max:
                diagnostics.append(f"Line {line}: {axis}{value:g} is above machine maximum {axis_max:g}.")
        return diagnostics

    def _validate_feed(self, feed_rate: float, line: int) -> list[str]:
        diagnostics = []
        min_feed = self.feed.get("min_feed")
        max_feed = self.feed.get("max_feed")
        if min_feed is not None and feed_rate < min_feed:
            diagnostics.append(f"Line {line}: Feed {feed_rate:g} is below minimum {min_feed:g}.")
        if max_feed is not None and feed_rate > max_feed:
            diagnostics.append(f"Line {line}: Feed {feed_rate:g} is above maximum {max_feed:g}.")
        return diagnostics

    def _validate_arc(self, node: ASTArc) -> list[str]:
        if self.capabilities.get("arcs", True):
            return []
        return [f"Line {node.line}: Arcs are not supported by {self.name}."]

    def _validate_spindle(self, node: ASTSpindle) -> list[str]:
        diagnostics = []
        if node.enabled and not self.capabilities.get("spindle", True):
            diagnostics.append(f"Line {node.line}: Spindle commands are not supported by {self.name}.")
        if node.speed is not None:
            min_rpm = self.spindle.get("min_rpm")
            max_rpm = self.spindle.get("max_rpm")
            if min_rpm is not None and node.speed < min_rpm:
                diagnostics.append(f"Line {node.line}: Spindle speed {node.speed:g} is below minimum {min_rpm:g}.")
            if max_rpm is not None and node.speed > max_rpm:
                diagnostics.append(f"Line {node.line}: Spindle speed {node.speed:g} is above maximum {max_rpm:g}.")
        return diagnostics

    def _validate_coolant(self, node: ASTCoolant) -> list[str]:
        diagnostics = []
        if node.flood and not self.capabilities.get("flood_coolant", True):
            diagnostics.append(f"Line {node.line}: Flood coolant is not supported by {self.name}.")
        if node.mist and not self.capabilities.get("mist_coolant", True):
            diagnostics.append(f"Line {node.line}: Mist coolant is not supported by {self.name}.")
        return diagnostics


def validate_ast_against_profile(ast: list[Any], machine_profile: MachineProfile | dict[str, Any] | None):
    if machine_profile is None:
        return
    profile = machine_profile if isinstance(machine_profile, MachineProfile) else MachineProfile(machine_profile)
    diagnostics = profile.validate_ast(ast)
    if diagnostics:
        raise ValidatorError("\n".join(diagnostics))
