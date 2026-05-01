from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ums_studio.transport.transport_registry import TransportRegistry


class ConnectionPanel(QWidget):
    def __init__(self, log_callback=None, parent=None):
        super().__init__(parent)
        self.registry = TransportRegistry()
        self.log_callback = log_callback
        self.transport = None

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.transport_combo = QComboBox()
        self.transport_combo.addItems(self.registry.list_transports())
        self.serial_port = QLineEdit("COM1")
        self.baud_rate = QLineEdit("115200")
        self.tcp_host = QLineEdit("127.0.0.1")
        self.tcp_port = QLineEdit("9000")

        form.addRow("Transport", self.transport_combo)
        form.addRow("Serial Port", self.serial_port)
        form.addRow("Baud", self.baud_rate)
        form.addRow("TCP Host", self.tcp_host)
        form.addRow("TCP Port", self.tcp_port)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.btn_connect = QPushButton("Connect")
        self.btn_disconnect = QPushButton("Disconnect")
        actions.addWidget(self.btn_connect)
        actions.addWidget(self.btn_disconnect)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.status = QLabel("Disconnected")
        layout.addWidget(self.status)

        self.btn_connect.clicked.connect(self.connect_transport)
        self.btn_disconnect.clicked.connect(self.disconnect_transport)
        self.transport_combo.currentTextChanged.connect(self._update_field_state)
        self._update_field_state(self.transport_combo.currentText())

    def connect_transport(self):
        self.disconnect_transport(log=False)
        name = self.transport_combo.currentText()
        try:
            if name == "serial":
                self.transport = self.registry.create(
                    "serial",
                    port=self.serial_port.text() or "COM1",
                    baud=int(self.baud_rate.text() or "115200"),
                )
            elif name == "tcp":
                self.transport = self.registry.create(
                    "tcp",
                    host=self.tcp_host.text() or "127.0.0.1",
                    port=int(self.tcp_port.text() or "9000"),
                )
            else:
                self.transport = self.registry.create("mock")

            self.transport.open()
            self.status.setText(f"Connected: {name}")
            self._log(f"Connected to {name} transport.")
        except Exception as exc:
            self.transport = None
            self.status.setText("Connection failed")
            self._log(f"Connection failed: {exc}")

    def disconnect_transport(self, log=True):
        if self.transport:
            try:
                self.transport.close()
            finally:
                self.transport = None
        self.status.setText("Disconnected")
        if log:
            self._log("Transport disconnected.")

    def current_transport(self):
        return self.transport

    def current_transport_name(self) -> str:
        return self.transport_combo.currentText().lower()

    def is_connected(self) -> bool:
        return self.transport is not None

    def _update_field_state(self, name: str):
        is_serial = name == "serial"
        is_tcp = name == "tcp"
        self.serial_port.setEnabled(is_serial)
        self.baud_rate.setEnabled(is_serial)
        self.tcp_host.setEnabled(is_tcp)
        self.tcp_port.setEnabled(is_tcp)

    def _log(self, message: str):
        if self.log_callback:
            self.log_callback(message)
