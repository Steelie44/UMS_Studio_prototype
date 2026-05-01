from pathlib import Path
import json

from PyQt6.QtWidgets import (
    QGroupBox,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTextEdit,
    QPushButton,
)

from ums_studio.ui.panels.machine_control_panel import MachineControlPanel
from ums_studio.ui.panels.execution_panel import ExecutionPanel
from ums_studio.ui.panels.compiler_panel import CompilerPanel
from ums_studio.ui.panels.connection_panel import ConnectionPanel
from ums_studio.ui.panels.project_selector import ProjectSelector
from ums_studio.ui.widgets.connection_indicator import ConnectionIndicator
from ums_studio.ui.widgets.console_widget import ConsoleWidget
from ums_studio.ui.panels.status_bar import StatusBar
from ums_studio.core.execution_controller import ExecutionController
from ums_studio.core.compiler import GCodeStreamer, NativePacketStreamer
from ums_studio.core.machine_session import MachineSession
from ums_studio.core.mock_machine import MockMachine
from ums_studio.core.runtime import Runtime
from ums_studio.planner.planner_registry import PlannerRegistry
from ums_studio.language.gcode_converter import convert_gcode_to_ums


class MainWindow(QMainWindow):
    def __init__(self, data_root: Path):
        super().__init__()

        self.data_root = Path(data_root)
        self.machine_profile = self._load_machine_profile()
        self.session = MachineSession()
        self.session.machine = MockMachine(self.session)
        self.planners = PlannerRegistry()
        self.runtime = Runtime(self.session, self.planners)
        self.exec_controller = ExecutionController(
            self.session,
            self.runtime,
            self._on_execution_line_changed,
            self._log,
        )

        self.setWindowTitle("UMS Studio")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        top_bar = QHBoxLayout()
        self.connection_indicator = ConnectionIndicator()
        top_bar.addWidget(self.connection_indicator)
        top_bar.addStretch(1)
        root.addLayout(top_bar)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        self.editor = QTextEdit()
        editor_page = QWidget()
        editor_layout = QVBoxLayout(editor_page)
        editor_actions = QHBoxLayout()
        self.btn_convert_gcode = QPushButton("Convert G-code to UMS")
        editor_actions.addWidget(self.btn_convert_gcode)
        editor_actions.addStretch(1)
        editor_layout.addLayout(editor_actions)
        editor_layout.addWidget(self.editor, 1)

        dashboard = QWidget()
        dashboard_layout = QHBoxLayout(dashboard)
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()

        self.connection_panel = ConnectionPanel(self._log)
        self.machine_panel = MachineControlPanel(self.session)
        self.execution_panel = ExecutionPanel(self.runtime, self.session)
        self.execution_panel.set_controls_visible(False)
        self.compiler_panel = CompilerPanel(
            self._editor_text,
            self._log,
            self._send_compiled_output,
            self._machine_profile,
        )

        left_column.addWidget(self._section("Connection", self.connection_panel))
        left_column.addWidget(self._section("Machine", self.machine_panel))
        left_column.addWidget(self._section("Job Progress", self.execution_panel))
        left_column.addStretch(1)
        right_column.addWidget(self._section("Compiler", self.compiler_panel))

        dashboard_layout.addLayout(left_column, 1)
        dashboard_layout.addLayout(right_column, 2)

        self.tabs.addTab(dashboard, "Dashboard")
        self.tabs.addTab(editor_page, "Editor")

        self.project_selector = ProjectSelector(
            self.data_root,
            self._on_project_loaded,
            self._log,
        )
        self.project_selector.on_folder_selected = self._on_project_folder_selected
        self.project_selector.on_open_selected = self._on_open_selected_project
        self.tabs.addTab(self.project_selector, "Projects")

        self.console = ConsoleWidget()
        self.console.setMaximumHeight(150)
        root.addWidget(self.console, 0)

        self.status_bar = StatusBar()
        root.addWidget(self.status_bar)
        self.session.set_log_callback(self._append_log)
        self.session.set_state_callback(self._on_machine_state)
        self.session.machine.start()

        self.machine_panel.on_cycle_start = self._on_cycle_start
        self.machine_panel.on_cycle_pause = self._on_cycle_pause
        self.machine_panel.on_cycle_stop = self._on_cycle_stop

        self.execution_panel.on_start = self._on_cycle_start
        self.execution_panel.on_pause = self._on_cycle_pause
        self.execution_panel.on_stop = self._on_cycle_stop
        self.btn_convert_gcode.clicked.connect(self._convert_editor_gcode_to_ums)

    def _log(self, msg: str):
        self._append_log(msg)

    def _append_log(self, msg: str):
        if hasattr(self, "console"):
            self.console.append_line(msg)
        if hasattr(self, "status_bar"):
            self.status_bar.log(msg)
        if not hasattr(self, "console"):
            print(msg)

    def _editor_text(self) -> str:
        return self.editor.toPlainText()

    def _machine_profile(self):
        return self.machine_profile

    def _load_machine_profile(self):
        profile_path = self.data_root / "machines" / "mock_machine_config.json"
        if not profile_path.exists():
            return None
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            self._log(f"Failed to load machine profile: {exc}")
            return None

    def _on_project_loaded(self, path: Path, data: str):
        self.editor.setPlainText(data)
        self._log(f"Loaded project: {path}")

    def _on_project_folder_selected(self, folder: str):
        import os

        files = []
        for name in os.listdir(folder):
            if name.lower().endswith(".ums"):
                files.append({"name": name, "path": os.path.join(folder, name)})
        self.project_selector.set_projects(files)
        self._log(f"Project folder: {folder}")

    def _on_open_selected_project(self, project):
        path = project["path"]
        try:
            with open(path, "r") as f:
                text = f.read()
        except Exception as e:
            self._log(f"Failed to open project: {e}")
            return
        self.editor.setPlainText(text)
        self._log(f"Opened project: {path}")
        self.execution_panel.set_total_lines(len(text.splitlines()))

    def _on_cycle_start(self):
        program_text = self.editor.toPlainText()
        if not program_text.strip():
            self._log("No program loaded.")
            return
        if self._is_mock_selected():
            self.exec_controller.set_speed_multiplier(2.0)
            if not self.compiler_panel.start_preview_run(speed_multiplier=2.0):
                self._log("Cycle start blocked: mock preview compile failed.")
                return
            self._log("Mock preview started at 2x speed.")
        else:
            self.exec_controller.set_speed_multiplier(1.0)
        self.exec_controller.load_program(program_text)
        self.execution_panel.set_total_lines(len(program_text.splitlines()))
        self.exec_controller.start()
        self._log("Cycle started.")

    def _on_cycle_pause(self):
        self.exec_controller.pause()
        if self._is_mock_selected():
            self.compiler_panel.pause_preview_run()
        self._log("Cycle paused.")

    def _on_cycle_stop(self):
        self.exec_controller.stop()
        if self._is_mock_selected():
            self.compiler_panel.stop_preview_run()
        self._log("Cycle stopped.")

    def _on_execution_line_changed(self, line: int):
        if hasattr(self.execution_panel, "set_current_line"):
            self.execution_panel.set_current_line(line)

    def _on_machine_state(self, state: dict):
        if hasattr(self.machine_panel, "update_state"):
            self.machine_panel.update_state(state)

    def _convert_editor_gcode_to_ums(self):
        source = self.editor.toPlainText()
        if not source.strip():
            self._log("No editor text to convert.")
            return

        converted = convert_gcode_to_ums(source)
        self.editor.setPlainText(converted)
        self._log("Converted editor G-code to UMS syntax.")

    def _is_mock_selected(self) -> bool:
        return self.connection_panel.current_transport_name() == "mock"

    def _send_compiled_output(self, output, target: str):
        transport = self.connection_panel.current_transport()
        if not transport:
            raise RuntimeError("No transport connected")

        if target == "stm32f4":
            wait_for_ack = self.connection_panel.current_transport_name() != "mock"
            NativePacketStreamer(transport, wait_for_ack=wait_for_ack).stream(output)
            self._log(f"Sent {len(output)} STM32F4 packet(s).")
            return

        if isinstance(output, str):
            if self.connection_panel.current_transport_name() == "mock":
                sent = 0
                for line in output.splitlines():
                    if line.strip():
                        transport.send_line(line)
                        sent += 1
                self._log(f"Sent {sent} G-code line(s) to mock transport.")
            else:
                GCodeStreamer(transport, target).stream(output)
                self._log(f"Sent G-code program for {target}.")
            return

        raise RuntimeError("Unsupported compiler output")

    def _section(self, title: str, widget: QWidget) -> QGroupBox:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(widget)
        return group
