from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ASTMove:
    axes: Dict[str, float]
    feed_rate: Optional[float]
    rapid: bool
    line: int


@dataclass
class ASTArc:
    axes: Dict[str, float]
    center_offset: Dict[str, float]
    clockwise: bool
    feed_rate: Optional[float]
    line: int


@dataclass
class ASTDwell:
    duration_ms: int
    line: int


@dataclass
class ASTSpindle:
    enabled: bool
    speed: int | None
    direction: str | None
    line: int


@dataclass
class ASTCoolant:
    flood: bool | None
    mist: bool | None
    line: int
