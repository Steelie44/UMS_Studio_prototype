from PyQt6.QtCore import QTimer
import math
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ums_studio.core.compiler import (
    collect_diagnostics,
    compile_ums,
    compile_ums_to_gcode,
    compile_ums_to_packets,
    build_preview_segments,
    render_diagnostics,
)
from ums_studio.ui.widgets.path_preview_widget import PathPreviewWidget


class CompilerPanel(QWidget):
    def __init__(
        self,
        get_source,
        log_callback=None,
        send_callback=None,
        machine_profile_provider=None,
        parent=None,
    ):
        super().__init__(parent)
        self.get_source = get_source
        self.log_callback = log_callback
        self.send_callback = send_callback
        self.machine_profile_provider = machine_profile_provider
        self.last_output = None
        self.last_target = None
        self.preview_points = []
        self.preview_index = 0
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self._advance_preview_run)
        self.preview_speed = 2

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.target_combo = QComboBox()
        self.target_combo.addItems(["stm32f4", "grbl", "linuxcnc", "marlin"])
        form.addRow("Target", self.target_combo)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.btn_compile = QPushButton("Compile")
        self.btn_send = QPushButton("Send")
        self.btn_compile_send = QPushButton("Compile + Send")
        self.btn_clear = QPushButton("Clear Output")
        actions.addWidget(self.btn_compile)
        actions.addWidget(self.btn_send)
        actions.addWidget(self.btn_compile_send)
        actions.addWidget(self.btn_clear)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.status = QLabel("Ready")
        layout.addWidget(self.status)

        self.diagnostics = QPlainTextEdit()
        self.diagnostics.setReadOnly(True)
        self.diagnostics.setMaximumHeight(110)
        self.diagnostics.setPlaceholderText("Diagnostics")
        layout.addWidget(self.diagnostics)

        self.preview = PathPreviewWidget()
        layout.addWidget(self.preview)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.output, 1)

        self.btn_compile.clicked.connect(self.compile_current_program)
        self.btn_send.clicked.connect(self.send_current_output)
        self.btn_compile_send.clicked.connect(self.compile_and_send)
        self.btn_clear.clicked.connect(self.clear_output)

    def compile_current_program(self):
        source = self.get_source() if self.get_source else ""
        target = self.target_combo.currentText()
        machine_profile = self._machine_profile()

        if not source.strip():
            self._set_status("No UMS program in the editor.")
            self.output.clear()
            self.diagnostics.setPlainText("ERROR: No UMS program in the editor.")
            return

        try:
            commands = compile_ums(source, machine_profile)
            segments = build_preview_segments(commands)
            self.preview.set_segments(segments)
            self.preview_points = self._flatten_segments(segments)
            self.preview_index = 0

            if target == "stm32f4":
                packets = compile_ums_to_packets(source, target, machine_profile)
                self.last_output = packets
                self.last_target = target
                rendered = self._render_packets(packets)
            else:
                rendered = compile_ums_to_gcode(source, target, machine_profile)
                self.last_output = rendered
                self.last_target = target

            self.output.setPlainText(rendered)
            self.diagnostics.setPlainText(render_diagnostics(collect_diagnostics(source, machine_profile)))
            self._set_status(f"Compiled for {target}: {len(source.splitlines())} source lines.")
        except Exception as exc:
            self.last_output = None
            self.last_target = None
            self.output.setPlainText(str(exc))
            self.preview.clear()
            self.preview_points = []
            self.preview_index = 0
            self.diagnostics.setPlainText(render_diagnostics(collect_diagnostics(source, machine_profile)))
            self._set_status(f"Compile failed for {target}.")
            return False

        return True

    def send_current_output(self):
        if self.last_output is None:
            self._set_status("Nothing compiled yet.")
            return False
        if not self.send_callback:
            self._set_status("No sender is available.")
            return False
        try:
            self.send_callback(self.last_output, self.last_target)
            self._set_status(f"Sent output for {self.last_target}.")
            return True
        except Exception as exc:
            self._set_status(f"Send failed: {exc}")
            return False

    def compile_and_send(self):
        if self.compile_current_program():
            self.send_current_output()

    def _render_packets(self, packets: list[bytes]) -> str:
        lines = []
        for index, packet in enumerate(packets, start=1):
            lines.append(f"{index:04d}: {packet.hex(' ')}")
        return "\n".join(lines)

    def clear_output(self):
        self.stop_preview_run()
        self.output.clear()
        self.diagnostics.clear()
        self.preview.clear()
        self.preview_points = []
        self.preview_index = 0
        self.last_output = None
        self.last_target = None
        self._set_status("Compiler output cleared.")

    def start_preview_run(self, speed_multiplier: float = 2.0):
        if not self.compile_current_program():
            return False
        if not self.preview_points:
            self._set_status("No preview path to run.")
            return False

        self.preview_speed = max(0.25, speed_multiplier)
        self.preview_index = 0
        self.preview.set_tool_position(self.preview_points[0])
        interval_ms = max(10, int(50 / self.preview_speed))
        self.preview_timer.start(interval_ms)
        self._set_status(f"Mock preview running at {self.preview_speed:g}x.")
        return True

    def pause_preview_run(self):
        if self.preview_timer.isActive():
            self.preview_timer.stop()
            self._set_status("Mock preview paused.")

    def stop_preview_run(self):
        if self.preview_timer.isActive():
            self.preview_timer.stop()
        self.preview_index = 0
        if self.preview_points:
            self.preview.set_tool_position(self.preview_points[0])

    def _advance_preview_run(self):
        if not self.preview_points:
            self.preview_timer.stop()
            return

        self.preview_index += 1
        if self.preview_index >= len(self.preview_points):
            self.preview_index = len(self.preview_points) - 1
            self.preview.set_tool_position(self.preview_points[self.preview_index])
            self.preview_timer.stop()
            self._set_status("Mock preview complete.")
            return

        self.preview.set_tool_position(self.preview_points[self.preview_index])

    def _flatten_segments(self, segments):
        points = []
        for segment in segments:
            segment_points = self._sample_segment_points(segment.points)
            if not segment_points:
                continue
            if points and points[-1] == segment_points[0]:
                segment_points = segment_points[1:]
            points.extend(segment_points)
        return points

    def _sample_segment_points(self, segment_points):
        if len(segment_points) < 2:
            return list(segment_points)

        sampled = [segment_points[0]]
        for start, end in zip(segment_points, segment_points[1:]):
            distance = math.hypot(end[0] - start[0], end[1] - start[1])
            steps = max(1, int(distance / 2.0))
            for step in range(1, steps + 1):
                t = step / steps
                sampled.append(
                    (
                        start[0] + (end[0] - start[0]) * t,
                        start[1] + (end[1] - start[1]) * t,
                    )
                )
        return sampled

    def _set_status(self, message: str):
        self.status.setText(message)
        if self.log_callback:
            self.log_callback(message)

    def _machine_profile(self):
        if self.machine_profile_provider:
            return self.machine_profile_provider()
        return None
