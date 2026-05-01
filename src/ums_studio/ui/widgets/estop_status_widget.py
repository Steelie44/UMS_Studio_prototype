from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class EStopStatusWidget(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session

        layout = QVBoxLayout(self)

        self.btn_estop = QPushButton("E-STOP")
        self.btn_reset = QPushButton("RESET")
        self.btn_estop.setStyleSheet(
            """
            QPushButton {
                background-color: #b91c1c;
                color: white;
                font-weight: bold;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #7f1d1d;
            }
            """
        )
        self.btn_reset.setStyleSheet(
            """
            QPushButton {
                background-color: #15803d;
                color: white;
                font-weight: bold;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QPushButton:pressed {
                background-color: #14532d;
            }
            """
        )

        layout.addWidget(self.btn_estop)
        layout.addWidget(self.btn_reset)

        self.btn_estop.clicked.connect(self._on_estop)
        self.btn_reset.clicked.connect(self._on_reset)

    def _on_estop(self):
        if self.session:
            if hasattr(self.session, "estop"):
                self.session.estop()

    def _on_reset(self):
        if self.session:
            if hasattr(self.session, "reset"):
                self.session.reset()


    # ------------------------------------------------------------
    # FAULT LIGHT UPDATE
    # ------------------------------------------------------------
    def set_fault_state(self, faulted: bool):
        if faulted:
            self.lbl_fault_light.setStyleSheet("""
                background-color: red;
                border-radius: 10px;
                border: 2px solid black;
            """)
        else:
            self.lbl_fault_light.setStyleSheet("""
                background-color: green;
                border-radius: 10px;
                border: 2px solid black;
            """)
