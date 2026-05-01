from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QStatusBar

class StatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        self._connection_status = "disconnected"
        self._last_message = "Ready"
        self._update_text()

    def log(self, msg: str):
        self._last_message = msg
        self._update_text()

    def set_connection_status(self, status: str):
        self._connection_status = status
        self._update_text()

    def _update_text(self):
        self.showMessage(f"[{self._connection_status}] {self._last_message}")
