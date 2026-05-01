from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class MoveCommand:
    axes: Dict[str, float]
    feed_rate: Optional[float]
    rapid: bool


@dataclass
class ArcCommand:
    axes: Dict[str, float]
    center_offset: Dict[str, float]
    clockwise: bool
    feed_rate: Optional[float]


@dataclass
class DwellCommand:
    duration_ms: int


@dataclass
class SpindleCommand:
    enabled: bool
    speed: int | None
    direction: str | None


@dataclass
class CoolantCommand:
    flood: bool | None
    mist: bool | None
