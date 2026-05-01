from dataclasses import dataclass
from typing import Dict


@dataclass
class LinearSegment:
    target: Dict[str, float]
    feed_rate: float
    rapid: bool = False


@dataclass
class ArcSegment:
    target: Dict[str, float]
    center_offset: Dict[str, float]
    clockwise: bool
    feed_rate: float


@dataclass
class DwellSegment:
    duration_ms: int


@dataclass
class SpindleSegment:
    enabled: bool
    speed: int | None
    direction: str | None


@dataclass
class CoolantSegment:
    flood: bool | None
    mist: bool | None
