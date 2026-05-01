import serial
from .transport_base import TransportBase


class SerialTransport(TransportBase):
    def __init__(self, port: str, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.ser = None

    def open(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            if self.ser.is_open:
                self._notify_status("connected")
            else:
                self._notify_status("error")
        except Exception as e:
            self._notify_status("error")
            raise


    def close(self) -> None:
        if self.ser:
            self.ser.close()
            self.ser = None

    def send_line(self, data: str | bytes) -> None:
        if self.ser:
            if isinstance(data, str):
                data = (data + "\n").encode("ascii")
            self.ser.write(data)

    def read_line(self) -> str | bytes:
        if not self.ser:
            return "ERR 0 999 NoSerial"
        first = self.ser.read(1)
        if first == b"\xAA":
            rest = self.ser.read(1)
            length = self.ser.read(1)[0]
            body = self.ser.read(length)
            return b"\xAA" + rest + bytes([length]) + body
        line = first + self.ser.readline()
        return line.decode("ascii", errors="ignore").strip()

    def _notify_status(self, status: str) -> None:
        callback = getattr(self, "on_status_change", None)
        if callback:
            callback(status)
