from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class DROWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.axes = ["X", "Y", "Z"]
        self.labels = {}
        self.feed_label = None
        self.spindle_label = None

        layout = QGridLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        font_axis = QFont("Consolas", 12, QFont.Weight.Bold)
        font_value = QFont("Consolas", 14)

        row = 0
        for axis in self.axes:
            lbl_axis = QLabel(axis)
            lbl_axis.setFont(font_axis)
            lbl_axis.setAlignment(Qt.AlignmentFlag.AlignLeft)

            lbl_val = QLabel("0.000")
            lbl_val.setFont(font_value)
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)

            layout.addWidget(lbl_axis, row, 0)
            layout.addWidget(lbl_val, row, 1)

            self.labels[axis] = lbl_val
            row += 1

        lbl_feed = QLabel("FEED")
        lbl_feed.setFont(font_axis)
        lbl_feed.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.feed_label = QLabel("0.0")
        self.feed_label.setFont(font_value)
        self.feed_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(lbl_feed, row, 0)
        layout.addWidget(self.feed_label, row, 1)
        row += 1

        lbl_spindle = QLabel("RPM")
        lbl_spindle.setFont(font_axis)
        lbl_spindle.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.spindle_label = QLabel("0")
        self.spindle_label.setFont(font_value)
        self.spindle_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(lbl_spindle, row, 0)
        layout.addWidget(self.spindle_label, row, 1)

        self.setLayout(layout)

    def set_axes(self, axes):
        self.axes = axes

    def update_positions(self, pos_dict):
        for axis, value in pos_dict.items():
            if axis in self.labels:
                self.labels[axis].setText(f"{value:.3f}")

    def update_feed(self, feed):
        if self.feed_label is not None and feed is not None:
            self.feed_label.setText(f"{feed:.1f}")

    def update_spindle(self, rpm):
        if self.spindle_label is not None and rpm is not None:
            self.spindle_label.setText(f"{int(rpm)}")

    def set_state_color(self, state):
        if state == "idle":
            color = "#ffffff"
        elif state == "running":
            color = "#00ff00"
        elif state == "homing":
            color = "#ffff00"
        elif state == "alarm":
            color = "#ff4444"
        else:
            color = "#cccccc"

        for lbl in list(self.labels.values()) + [self.feed_label, self.spindle_label]:
            if lbl is not None:
                lbl.setStyleSheet(f"color: {color};")
