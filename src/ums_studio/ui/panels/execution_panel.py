from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QProgressBar


class ExecutionPanel(QWidget):
    def __init__(self, runtime, session, parent=None):
        super().__init__(parent)
        self.runtime = runtime
        self.session = session
        self.on_start = None
        self.on_pause = None
        self.on_stop = None

        layout = QVBoxLayout(self)

        self.label_status = QLabel("Idle")
        layout.addWidget(self.label_status)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.controls_row = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_pause = QPushButton("Pause")
        self.btn_stop = QPushButton("Stop")

        self.controls_row.addWidget(self.btn_start)
        self.controls_row.addWidget(self.btn_pause)
        self.controls_row.addWidget(self.btn_stop)

        layout.addLayout(self.controls_row)

        self.btn_start.clicked.connect(self._start)
        self.btn_pause.clicked.connect(self._pause)
        self.btn_stop.clicked.connect(self._stop)

    def set_total_lines(self, n):
        self.progress.setMaximum(max(1, n))
        self.progress.setValue(0)

    def set_current_line(self, n):
        self.progress.setValue(max(0, n))

    def set_controls_visible(self, visible: bool):
        self.btn_start.setVisible(visible)
        self.btn_pause.setVisible(visible)
        self.btn_stop.setVisible(visible)

    def start_cycle(self):
        self._start()

    def pause_cycle(self):
        self._pause()

    def stop_cycle(self):
        self._stop()

    def _start(self):
        self.label_status.setText("Running")
        if self.on_start:
            self.on_start()

    def _pause(self):
        self.label_status.setText("Paused")
        if self.on_pause:
            self.on_pause()

    def _stop(self):
        self.label_status.setText("Stopped")
        if self.on_stop:
            self.on_stop()
