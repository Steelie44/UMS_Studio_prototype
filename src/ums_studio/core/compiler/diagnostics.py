from dataclasses import dataclass
import re
from typing import Any

from .machine_profile import validate_ast_against_profile
from ...language.parser import Parser
from ...language.tokenizer import Tokenizer
from ...language.validator import Validator


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    message: str
    line: int | None = None


def collect_diagnostics(source: str, machine_profile: Any = None) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    try:
        tokens = Tokenizer().tokenize(source)
        ast = Parser().parse(tokens)
        validate_ast_against_profile(ast, machine_profile)
        Validator().validate(ast)
    except Exception as exc:
        for message in str(exc).splitlines() or [str(exc)]:
            diagnostics.append(Diagnostic("error", message, _extract_line(message)))

    if not diagnostics:
        diagnostics.append(Diagnostic("info", "No diagnostics. Program is valid."))
    return diagnostics


def render_diagnostics(diagnostics: list[Diagnostic]) -> str:
    lines = []
    for diagnostic in diagnostics:
        prefix = diagnostic.severity.upper()
        if diagnostic.line is not None:
            lines.append(f"{prefix} line {diagnostic.line}: {diagnostic.message}")
        else:
            lines.append(f"{prefix}: {diagnostic.message}")
    return "\n".join(lines)


def _extract_line(message: str) -> int | None:
    match = re.search(r"[Ll]ine\s+(\d+)", message)
    if not match:
        return None
    return int(match.group(1))
