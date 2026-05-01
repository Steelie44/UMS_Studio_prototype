from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AxisState:
    position: float = 0.0


@dataclass
class MachineState:
    axes: Dict[str, AxisState] = field(default_factory=lambda: {a: AxisState() for a in "XYZ"})
    feed_rate: float = 0.0
    spindle_rpm: int = 0
   

def default_state() -> MachineState:
    """Create a default machine state."""
    return MachineState()
