from typing import List, Any, Dict
from .ast_nodes import ASTMove, ASTArc, ASTDwell, ASTSpindle, ASTCoolant
from .validator_rules import MODAL_GROUPS, FEED_REQUIRED_FOR
from .language_spec import AXES, ARC_OFFSETS
from ..core.command_model import MoveCommand, ArcCommand, DwellCommand, SpindleCommand, CoolantCommand
from ..core.errors import ValidatorError


class Validator:
    def __init__(self):
        self.modal_state: Dict[str, str] = {}

    def validate(self, ast_list: List[Any]) -> List[Any]:
        commands: List[Any] = []
        for node in ast_list:
            t = self._determine_type(node)
            self._apply_modal_rules(node)
            commands.append(self._convert(node))
        return commands

    def _determine_type(self, node) -> str:
        if isinstance(node, ASTMove):
            return "move"
        if isinstance(node, ASTArc):
            return "arc"
        if isinstance(node, ASTDwell):
            return "dwell"
        if isinstance(node, ASTSpindle):
            return "spindle"
        if isinstance(node, ASTCoolant):
            return "coolant"
        raise ValidatorError(f"Unknown AST node {type(node)}")

    def _apply_modal_rules(self, node):
        code = getattr(node, "code", None)
        if code is None:
            raise ValidatorError("AST node missing .code")
        for group, cmds in MODAL_GROUPS.items():
            if code in cmds:
                self.modal_state[group] = code

    def _convert(self, node):
        if isinstance(node, ASTMove):
            self._validate_move(node)
            return MoveCommand(axes=node.axes, feed_rate=node.feed_rate, rapid=node.rapid)
        if isinstance(node, ASTArc):
            self._validate_arc(node)
            return ArcCommand(axes=node.axes, center_offset=node.center_offset, clockwise=node.clockwise, feed_rate=node.feed_rate)
        if isinstance(node, ASTDwell):
            self._validate_dwell(node)
            return DwellCommand(duration_ms=node.duration_ms)
        if isinstance(node, ASTSpindle):
            return SpindleCommand(enabled=node.enabled, speed=node.speed, direction=node.direction)
        if isinstance(node, ASTCoolant):
            return CoolantCommand(flood=node.flood, mist=node.mist)
        raise ValidatorError(f"Unknown AST node {type(node)}")

    def _validate_move(self, node: ASTMove):
        for axis in node.axes.keys():
            if axis not in AXES:
                raise ValidatorError(f"Invalid axis {axis} on line {node.line}")
        if not node.rapid and node.feed_rate is None:
            raise ValidatorError(f"G1 move missing feed rate on line {node.line}")

    def _validate_arc(self, node: ASTArc):
        for off in ARC_OFFSETS:
            if off not in node.center_offset:
                raise ValidatorError(f"Arc missing {off} on line {node.line}")
        if node.feed_rate is None:
            raise ValidatorError(f"Arc missing feed rate on line {node.line}")

    def _validate_dwell(self, node: ASTDwell):
        if node.duration_ms <= 0:
            raise ValidatorError(f"Dwell must be > 0 ms on line {node.line}")
