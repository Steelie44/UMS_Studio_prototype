# UMS Studio

UMS Studio is a development environment for **UMS, Unified Machine Script**: a deterministic, hardware-aware motion-control language for CNC machines, 3D printers, robotics platforms, and embedded motion systems.

The goal of UMS is to provide a safer and more explicit alternative to traditional G-code workflows. Instead of relying on modal machine state, ambiguous dialect behavior, and controller-specific quirks, UMS is designed around a clear command model that can be validated, previewed, compiled, and streamed to different machine targets.

UMS Studio is the reference application and testing ground for that language.

## Why UMS?

Traditional G-code is powerful, but it carries decades of legacy assumptions:

- commands can depend on hidden modal state
- different controllers interpret similar commands differently
- validation usually happens too late, often at the machine
- machine limits and capabilities are not always part of the program workflow
- testing and previewing are frequently separated from execution

UMS aims to make motion programs easier to reason about before they reach hardware.

Example UMS-style syntax:

```text
RAPID X0 Y0 Z0
MOVE X10 Y5 F300
DWELL 500ms
SPINDLE CW S1200
COOLANT FLOOD
```

UMS Studio can still accept a G-code-shaped syntax while the language evolves:

```gcode
G0 X0 Y0 Z0
G1 X10 Y5 F300
G4 P500
M3 S1200
M8
```

## Current Features

UMS Studio currently includes:

- a PyQt6 desktop interface
- UMS program editor
- compiler panel with target selection
- readable diagnostics for parser, validation, and machine profile errors
- XY job preview for rapid, feed, and arc moves
- mock machine dashboard with DRO
- jog controls for X/Y/Z axes
- home and zero controls
- cycle start, pause, and stop controls
- E-stop and reset controls
- console logging for UI actions
- connection panel for mock, serial, and TCP transports
- compile, send, and compile-and-send workflow
- STM32F4 native packet output
- G-code output for GRBL, LinuxCNC, and Marlin
- starter pytest coverage for compiler behavior

## Target Backends

UMS Studio currently supports two output paths.

### Native STM32F4 Packets

For custom firmware targets, UMS can compile directly into a binary packet protocol intended for STM32F4-based controllers.

This path is useful for building a native UMS firmware stack instead of translating through legacy G-code.

### G-code Targets

UMS can also compile into controller-specific G-code for:

- GRBL
- LinuxCNC
- Marlin

The compiler accounts for target differences such as dwell units and coolant/fan command behavior.

## Machine Profiles

Machine profiles describe the physical and logical capabilities of a target machine. They are used to validate programs before output is generated.

Profiles can define:

- supported axes
- axis min/max limits
- homing behavior
- steps per millimeter
- feed rate limits
- spindle RPM limits
- arc/spindle/coolant capabilities
- transport defaults

Example validation:

```text
MOVE X250 F100
```

If the current machine profile only allows `X` up to `200`, UMS Studio reports:

```text
ERROR line 1: Line 1: X250 is above machine maximum 200.
```

## Job Preview

The compiler panel includes a basic XY preview:

- rapid moves are shown as gray dashed lines
- feed moves are shown as blue lines
- arcs are shown as green curves

This is intentionally simple for now, but it gives immediate feedback about program shape before sending commands to a machine.

## Running UMS Studio

From PowerShell:

```powershell
cd "C:\Users\Jonathan\Desktop\UMS Studio\UMS Working Copy"
$env:PYTHONPATH = ".\src"
python -m ums_studio
```

If dependencies are missing, install the project first:

```powershell
python -m pip install -e .
```

For development tools and tests:

```powershell
python -m pip install -e ".[dev]"
```

## Running Tests

```powershell
cd "C:\Users\Jonathan\Desktop\UMS Studio\UMS Working Copy"
$env:PYTHONPATH = ".\src"
python -m pytest -q
```

Current starter tests cover:

- UMS-style syntax compilation
- GRBL G-code output
- STM32F4 packet output
- machine profile diagnostics
- unsafe move rejection
- preview segment generation

## Project Structure

```text
src/ums_studio/
  app/                  Host-side helpers and protocols
  core/                 Command model, runtime, compiler, mock machine
  core/compiler/        UMS compile pipelines, emitters, diagnostics, preview
  firmware/             Embedded protocol and firmware-side C stubs
  language/             Tokenizer, parser, AST, validator, language spec
  planner/              Motion planning helpers
  transport/            Mock, serial, and TCP transport layer
  ui/                   PyQt6 user interface
data/machines/          Machine profile JSON files
tests/                  Pytest coverage
```

## Status

UMS Studio is early-stage software. It is currently suitable for:

- language experimentation
- compiler development
- UI prototyping
- mock machine testing
- STM32F4 protocol development
- validating motion-control ideas before hardware integration

It is not yet a production machine controller. Hardware execution should be treated carefully until motion planning, safety interlocks, firmware handlers, and transport acknowledgements are fully implemented and tested.

## Roadmap

Planned improvements include:

- richer UMS language syntax
- editor line highlighting for diagnostics
- machine profile selection in the UI
- real serial port discovery
- STM32F4 firmware command execution handlers
- stronger motion planning and acceleration limits
- feed and spindle overrides
- 3D preview support
- safer send/stream state management
- broader test coverage

## Vision

UMS is intended to become a universal motion-control layer: readable enough for humans, strict enough for machines, and portable enough to target different controllers without rewriting programs for every firmware dialect.

UMS Studio is where that vision is being designed, tested, and proven.
