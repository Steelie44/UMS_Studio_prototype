AXES = ["X", "Y", "Z"]
ARC_OFFSETS = ["I", "J"]

LANGUAGE_SPEC = {
    "G0": {"type": "move", "rapid": True},
    "G1": {"type": "move", "rapid": False},
    "G2": {"type": "arc", "clockwise": True},
    "G3": {"type": "arc", "clockwise": False},
    "G4": {"type": "dwell"},
    "M3": {"type": "spindle", "enabled": True, "direction": "CW"},
    "M4": {"type": "spindle", "enabled": True, "direction": "CCW"},
    "M5": {"type": "spindle", "enabled": False},
    "M7": {"type": "coolant", "flood": False, "mist": True},
    "M8": {"type": "coolant", "flood": True, "mist": False},
    "M9": {"type": "coolant", "flood": False, "mist": False},
    "RAPID": {"type": "move", "rapid": True},
    "MOVE": {"type": "move", "rapid": False},
    "ARC_CW": {"type": "arc", "clockwise": True},
    "ARC_CCW": {"type": "arc", "clockwise": False},
    "DWELL": {"type": "dwell"},
    "SPINDLE": {"type": "spindle", "enabled": True, "direction": "CW"},
    "COOLANT": {"type": "coolant"},
}
