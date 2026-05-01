from dataclasses import dataclass


@dataclass(frozen=True)
class TargetProfile:
    name: str
    header: tuple[str, ...]
    footer: tuple[str, ...]
    dwell_uses_milliseconds: bool
    flood_coolant_on: str
    coolant_off: str
    supports_mist_coolant: bool
    supports_spindle_ccw: bool
    requires_line_ack: bool


TARGETS = {
    "grbl": TargetProfile(
        name="grbl",
        header=("G21", "G90", "G17"),
        footer=("M5", "M9"),
        dwell_uses_milliseconds=False,
        flood_coolant_on="M8",
        coolant_off="M9",
        supports_mist_coolant=True,
        supports_spindle_ccw=True,
        requires_line_ack=True,
    ),
    "linuxcnc": TargetProfile(
        name="linuxcnc",
        header=("G21", "G90", "G17"),
        footer=("M5", "M9", "M2"),
        dwell_uses_milliseconds=False,
        flood_coolant_on="M8",
        coolant_off="M9",
        supports_mist_coolant=True,
        supports_spindle_ccw=True,
        requires_line_ack=False,
    ),
    "marlin": TargetProfile(
        name="marlin",
        header=("G21", "G90"),
        footer=("M5", "M107"),
        dwell_uses_milliseconds=True,
        flood_coolant_on="M106",
        coolant_off="M107",
        supports_mist_coolant=False,
        supports_spindle_ccw=False,
        requires_line_ack=True,
    ),
}


def get_target(name: str) -> TargetProfile:
    key = name.lower()
    try:
        return TARGETS[key]
    except KeyError as exc:
        supported = ", ".join(sorted(TARGETS))
        raise ValueError(f"Unsupported target '{name}'. Supported targets: {supported}") from exc
