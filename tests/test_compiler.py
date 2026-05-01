import pytest

from ums_studio.core.compiler import (
    collect_diagnostics,
    compile_ums,
    compile_ums_to_gcode,
    compile_ums_to_packets,
    build_preview_segments,
)
from ums_studio.language.gcode_converter import convert_gcode_to_ums


PROFILE = {
    "name": "Test CNC",
    "axes": {
        "X": {"min": 0, "max": 50},
        "Y": {"min": 0, "max": 50},
        "Z": {"min": -10, "max": 10},
    },
    "feed": {"min_feed": 1, "max_feed": 500},
    "spindle": {"min_rpm": 0, "max_rpm": 12000},
    "capabilities": {
        "arcs": True,
        "spindle": True,
        "flood_coolant": True,
        "mist_coolant": False,
    },
}


def test_new_ums_syntax_compiles_to_gcode():
    source = "\n".join(
        [
            "RAPID X0 Y0 Z0",
            "MOVE X10 Y5 F300",
            "DWELL 500ms",
            "SPINDLE CW S1200",
            "COOLANT FLOOD",
        ]
    )

    gcode = compile_ums_to_gcode(source, "grbl", PROFILE)

    assert "G0 X0 Y0 Z0" in gcode
    assert "G1 X10 Y5 F300" in gcode
    assert "G4 P0.5" in gcode
    assert "M3 S1200" in gcode
    assert "M8" in gcode


def test_stm32f4_packet_compile_produces_binary_packets():
    packets = compile_ums_to_packets("RAPID X0 Y0\nMOVE X1 F100\n", "stm32f4", PROFILE)

    assert len(packets) == 2
    assert packets[0].startswith(b"\xAA\x55")


def test_machine_profile_reports_bounds_and_capabilities():
    diagnostics = collect_diagnostics("MOVE X60 F900\nCOOLANT MIST\n", PROFILE)
    messages = [diagnostic.message for diagnostic in diagnostics]

    assert any("above machine maximum" in message for message in messages)
    assert any("above maximum" in message for message in messages)
    assert any("Mist coolant is not supported" in message for message in messages)


def test_profile_validation_blocks_compile():
    with pytest.raises(Exception, match="above machine maximum"):
        compile_ums("MOVE X60 F100\n", PROFILE)


def test_preview_segments_include_rapid_feed_and_arc():
    commands = compile_ums(
        "\n".join(
            [
                "RAPID X5 Y0",
                "MOVE X10 Y0 F100",
                "ARC_CW X10 Y10 I0 J5 F100",
            ]
        ),
        PROFILE,
    )

    segments = build_preview_segments(commands)

    assert [segment.kind for segment in segments] == ["rapid", "feed", "arc"]
    assert len(segments[-1].points) > 2


def test_gcode_to_ums_converter_keeps_supported_motion_semantics():
    converted = convert_gcode_to_ums(
        "\n".join(
            [
                "G0 X0 Y0",
                "G1 X10 Y5 F300",
                "G2 X10 Y10 I0 J5 F100",
                "G4 P500",
                "M3 S1200",
                "M8",
                "M5",
            ]
        )
    )

    assert "RAPID X0 Y0" in converted
    assert "MOVE X10 Y5 F300" in converted
    assert "ARC_CW X10 Y10 I0 J5 F100" in converted
    assert "DWELL 500ms" in converted
    assert "SPINDLE CW S1200" in converted
    assert "COOLANT FLOOD" in converted
    assert "SPINDLE OFF" in converted
