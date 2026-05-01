import socket
from .transport_base import TransportBase


class TCPTransport(TransportBase):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = None

    def open(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def close(self) -> None:
        if self.sock:
            self.sock.close()
            self.sock = None

    def send_line(self, data: str | bytes) -> None:
        if not self.sock:
            return
        if isinstance(data, str):
            data = (data + "\n").encode("ascii")
        self.sock.sendall(data)

    def read_line(self) -> str | bytes:
        if not self.sock:
            return "ERR 0 999 NoSocket"
        first = self.sock.recv(1)
        if first == b"\xAA":
            rest = self.sock.recv(1)
            length = self.sock.recv(1)[0]
            body = self.sock.recv(length)
            return b"\xAA" + rest + bytes([length]) + body
        data = first
        while not data.endswith(b"\n"):
            data += self.sock.recv(1)
        return data.decode("ascii", errors="ignore").strip()
