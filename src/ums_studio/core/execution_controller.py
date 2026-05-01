from PyQt6.QtCore import QObject, QTimer

class ExecutionController(QObject):
    def __init__(self, session, runtime, update_line_callback, log_callback, parent=None):
        super().__init__(parent)
        self.session = session
        self.runtime = runtime
        self.update_line_callback = update_line_callback
        self.log_callback = log_callback

        self.program_lines = []
        self.current_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step)
        self.interval_ms = 100

    def load_program(self, text):
        self.program_lines = [l for l in text.splitlines()]
        self.current_index = 0

    def start(self):
        if not self.program_lines:
            return
        self.current_index = 0
        self._emit_line()
        self.timer.start(self.interval_ms)

    def pause(self):
        self.timer.stop()

    def stop(self):
        self.timer.stop()
        self.current_index = 0
        self._emit_line(reset=True)

    def set_speed_multiplier(self, multiplier: float):
        multiplier = max(0.25, multiplier)
        self.interval_ms = max(10, int(100 / multiplier))
        if self.timer.isActive():
            self.timer.start(self.interval_ms)

    def _step(self):
        if self.current_index >= len(self.program_lines):
            self.timer.stop()
            return
        line = self.program_lines[self.current_index]
        if self.log_callback:
            self.log_callback(f"EXEC {self.current_index + 1}: {line}")
        self._execute_line(line)
        self.current_index += 1
        self._emit_line()

    def _emit_line(self, reset=False):
        if reset:
            if self.update_line_callback:
                self.update_line_callback(0)
            return
        if self.update_line_callback:
            self.update_line_callback(self.current_index + 1)

    def _execute_line(self, line):
        if self.session:
            self.session.log(f"[UMS] {line}")
