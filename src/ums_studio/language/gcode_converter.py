GCODE_TO_UMS = {
    "G0": "RAPID",
    "G00": "RAPID",
    "G1": "MOVE",
    "G01": "MOVE",
    "G2": "ARC_CW",
    "G02": "ARC_CW",
    "G3": "ARC_CCW",
    "G03": "ARC_CCW",
    "M5": "SPINDLE OFF",
    "M05": "SPINDLE OFF",
    "M7": "COOLANT MIST",
    "M07": "COOLANT MIST",
    "M8": "COOLANT FLOOD",
    "M08": "COOLANT FLOOD",
    "M9": "COOLANT OFF",
    "M09": "COOLANT OFF",
}


def convert_gcode_to_ums(source: str) -> str:
    lines = []
    for raw_line in source.splitlines():
        code, comment = _split_comment(raw_line)
        stripped = code.strip()
        if not stripped:
            lines.append(raw_line)
            continue

        words = stripped.split()
        command = words[0].upper()
        args = words[1:]

        converted = _convert_command(command, args)
        if converted is None:
            converted = stripped

        if comment:
            converted = f"{converted} ;{comment}"
        lines.append(converted)

    return "\n".join(lines)


def _convert_command(command: str, args: list[str]) -> str | None:
    if command in ("G4", "G04"):
        return _convert_dwell(args)
    if command in ("M3", "M03", "M4", "M04"):
        return _convert_spindle(command, args)

    ums_command = GCODE_TO_UMS.get(command)
    if not ums_command:
        return None
    if args:
        return f"{ums_command} {' '.join(arg.upper() for arg in args)}"
    return ums_command


def _convert_dwell(args: list[str]) -> str:
    if not args:
        return "DWELL 0ms"

    first = args[0].upper()
    if first.startswith("P"):
        value = first[1:].lstrip("=")
        return f"DWELL {value}ms"
    if first.startswith("S"):
        value = first[1:].lstrip("=")
        return f"DWELL {value}s"
    return f"DWELL {first}"


def _convert_spindle(command: str, args: list[str]) -> str:
    direction = "CCW" if command in ("M4", "M04") else "CW"
    speed = None
    for arg in args:
        upper = arg.upper()
        if upper.startswith("S"):
            speed = upper
            break

    if speed:
        return f"SPINDLE {direction} {speed}"
    return f"SPINDLE {direction}"


def _split_comment(line: str) -> tuple[str, str]:
    if ";" not in line:
        return line, ""
    code, comment = line.split(";", 1)
    return code, comment
