from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from ums_studio.ui.widgets.dro_widget import DROWidget
from ums_studio.ui.widgets.estop_status_widget import EStopStatusWidget


class MachineControlPanel(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session

        self.on_cycle_start = None
        self.on_cycle_pause = None
        self.on_cycle_stop = None

        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        self.dro = DROWidget()
        top_row.addWidget(self.dro)
        layout.addLayout(top_row)

        self.step_size = QDoubleSpinBox()
        self.step_size.setRange(0.001, 1000.0)
        self.step_size.setDecimals(3)
        self.step_size.setValue(1.0)
        self.step_size.setSuffix(" mm")

        step_row = QHBoxLayout()
        step_row.addWidget(QLabel("Jog Step"))
        step_row.addWidget(self.step_size)
        step_row.addStretch(1)
        layout.addLayout(step_row)

        jog_grid = QGridLayout()
        jog_grid.addWidget(QLabel("Axis"), 0, 0)
        jog_grid.addWidget(QLabel("Negative"), 0, 1)
        jog_grid.addWidget(QLabel("Positive"), 0, 2)
        jog_grid.addWidget(QLabel("Home"), 0, 3)
        jog_grid.addWidget(QLabel("Zero"), 0, 4)

        for row_index, axis in enumerate(("X", "Y", "Z"), start=1):
            jog_grid.addWidget(QLabel(axis), row_index, 0)

            btn_negative = QPushButton(f"{axis}-")
            btn_positive = QPushButton(f"{axis}+")
            btn_home = QPushButton("Home")
            btn_zero = QPushButton("Zero")

            btn_negative.clicked.connect(lambda checked=False, a=axis: self._jog(a, -1))
            btn_positive.clicked.connect(lambda checked=False, a=axis: self._jog(a, 1))
            btn_home.clicked.connect(lambda checked=False, a=axis: self._home(a))
            btn_zero.clicked.connect(lambda checked=False, a=axis: self._zero(a))

            jog_grid.addWidget(btn_negative, row_index, 1)
            jog_grid.addWidget(btn_positive, row_index, 2)
            jog_grid.addWidget(btn_home, row_index, 3)
            jog_grid.addWidget(btn_zero, row_index, 4)

        layout.addLayout(jog_grid)

        row = QHBoxLayout()
        self.btn_cycle_start = QPushButton("Cycle Start")
        self.btn_cycle_pause = QPushButton("Pause")
        self.btn_cycle_stop = QPushButton("Stop")

        self.btn_cycle_start.clicked.connect(self._on_cycle_start_clicked)
        self.btn_cycle_pause.clicked.connect(self._on_cycle_pause_clicked)
        self.btn_cycle_stop.clicked.connect(self._on_cycle_stop_clicked)

        row.addWidget(self.btn_cycle_start)
        row.addWidget(self.btn_cycle_pause)
        row.addWidget(self.btn_cycle_stop)

        layout.addLayout(row)

        self.estop = EStopStatusWidget(self.session)
        layout.addWidget(self.estop)

    def _on_cycle_start_clicked(self):
        if self.on_cycle_start:
            self.on_cycle_start()

    def _on_cycle_pause_clicked(self):
        if self.on_cycle_pause:
            self.on_cycle_pause()

    def _on_cycle_stop_clicked(self):
        if self.on_cycle_stop:
            self.on_cycle_stop()

    def _jog(self, axis: str, direction: int):
        if self.session and hasattr(self.session, "jog"):
            self.session.jog(axis, direction, self.step_size.value())

    def _home(self, axis: str):
        if self.session and hasattr(self.session, "home"):
            self.session.home(axis)

    def _zero(self, axis: str):
        if self.session and hasattr(self.session, "zero"):
            self.session.zero(axis)

    def update_state(self, state: dict):
        position = {}
        for axis in ("X", "Y", "Z"):
            if axis in state:
                position[axis] = state[axis]
            elif axis.lower() in state:
                position[axis] = state[axis.lower()]

        if position:
            self.dro.update_positions(position)
        if "feed_rate" in state:
            self.dro.update_feed(state["feed_rate"])
        if "spindle_rpm" in state:
            self.dro.update_spindle(state["spindle_rpm"])
