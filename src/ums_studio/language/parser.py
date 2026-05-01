from typing import List, Dict, Any
from .tokenizer import Token
from .ast_nodes import ASTMove, ASTArc, ASTDwell, ASTSpindle, ASTCoolant
from .language_spec import LANGUAGE_SPEC, AXES, ARC_OFFSETS
from ..core.errors import ParserError


class Parser:
    def parse(self, tokens: List[Token]) -> List[Any]:
        ast: List[Any] = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.type != "WORD":
                raise ParserError(f"Expected command at line {tok.line}")
            code = tok.value.upper()
            if code not in LANGUAGE_SPEC:
                raise ParserError(f"Unknown command {code} on line {tok.line}")
            spec = LANGUAGE_SPEC[code]
            t = spec["type"]
            if t == "move":
                node, i = self._parse_move(tokens, i, code)
            elif t == "arc":
                node, i = self._parse_arc(tokens, i, code)
            elif t == "dwell":
                node, i = self._parse_dwell(tokens, i, code)
            elif t == "spindle":
                node, i = self._parse_spindle(tokens, i, code)
            elif t == "coolant":
                node, i = self._parse_coolant(tokens, i, code)
            else:
                raise ParserError(f"Unhandled type {t}")
            node.code = code
            ast.append(node)
        return ast

    def _parse_move(self, tokens, i, code):
        axes: Dict[str, float] = {}
        feed = None
        line = tokens[i].line
        spec = LANGUAGE_SPEC[code]
        rapid = spec.get("rapid", False)
        i += 1
        while i < len(tokens) and tokens[i].type == "WORD":
            part = tokens[i].value.upper()
            key, value = self._split_word(part)
            if key in AXES:
                axes[key] = self._parse_float(value, tokens[i].line, key)
            elif key == "F":
                feed = self._parse_float(value, tokens[i].line, key)
            else:
                break
            i += 1
        return ASTMove(axes=axes, feed_rate=feed, rapid=rapid, line=line), i

    def _parse_arc(self, tokens, i, code):
        spec = LANGUAGE_SPEC[code]
        clockwise = spec["clockwise"]
        axes: Dict[str, float] = {}
        offsets: Dict[str, float] = {}
        feed = None
        line = tokens[i].line
        i += 1
        while i < len(tokens) and tokens[i].type == "WORD":
            part = tokens[i].value.upper()
            key, value = self._split_word(part)
            if key in AXES:
                axes[key] = self._parse_float(value, tokens[i].line, key)
            elif key in ARC_OFFSETS:
                offsets[key] = self._parse_float(value, tokens[i].line, key)
            elif key == "F":
                feed = self._parse_float(value, tokens[i].line, key)
            else:
                break
            i += 1
        return ASTArc(axes=axes, center_offset=offsets, clockwise=clockwise, feed_rate=feed, line=line), i

    def _parse_dwell(self, tokens, i, code):
        line = tokens[i].line
        i += 1
        duration = 0
        if i < len(tokens) and tokens[i].type == "WORD":
            part = tokens[i].value.upper()
            if part.startswith("P"):
                duration = int(float(part[1:].lstrip("=")))
                i += 1
            elif part.endswith("MS"):
                duration = int(float(part[:-2]))
                i += 1
            elif part.endswith("S"):
                duration = int(float(part[:-1]) * 1000)
                i += 1
            else:
                duration = int(float(part))
                i += 1
        return ASTDwell(duration_ms=duration, line=line), i

    def _parse_spindle(self, tokens, i, code):
        spec = LANGUAGE_SPEC[code]
        line = tokens[i].line
        enabled = spec.get("enabled", True)
        direction = spec.get("direction")
        speed = None
        i += 1
        while i < len(tokens) and tokens[i].type == "WORD":
            part = tokens[i].value.upper()
            if part in ("OFF", "STOP"):
                enabled = False
            elif part in ("ON", "CW"):
                enabled = True
                direction = "CW"
            elif part == "CCW":
                enabled = True
                direction = "CCW"
            elif part.startswith("S"):
                speed = int(part[1:])
            elif part.isdigit():
                speed = int(part)
            else:
                break
            i += 1
        return ASTSpindle(enabled=enabled, speed=speed, direction=direction, line=line), i

    def _parse_coolant(self, tokens, i, code):
        spec = LANGUAGE_SPEC[code]
        line = tokens[i].line
        flood = spec.get("flood")
        mist = spec.get("mist")
        i += 1
        if code == "COOLANT":
            flood = False
            mist = False
            while i < len(tokens) and tokens[i].type == "WORD":
                part = tokens[i].value.upper()
                if part in ("OFF", "STOP"):
                    flood = False
                    mist = False
                elif part in ("ON", "FLOOD"):
                    flood = True
                    mist = False
                elif part == "MIST":
                    flood = False
                    mist = True
                else:
                    break
                i += 1
        return ASTCoolant(flood=flood, mist=mist, line=line), i

    def _split_word(self, part: str):
        if "=" in part:
            key, value = part.split("=", 1)
            return key, value
        return part[0], part[1:]

    def _parse_float(self, value: str, line: int, name: str) -> float:
        try:
            return float(value)
        except ValueError as exc:
            raise ParserError(f"Invalid value for {name} on line {line}") from exc
