from .transport_base import TransportBase


class MockTransport(TransportBase):
    def __init__(self):
        self.opened = False
        self.counter = 0

    def open(self) -> None:
        self.opened = True

    def close(self) -> None:
        self.opened = False

    def send_line(self, line: str) -> None:
        pass

    def read_line(self) -> str:
        self.counter += 1

        if self.counter % 10 == 0:
            return 'EVENT {"type":"limit","axis":"X"}'

        if self.counter % 15 == 0:
            return 'EVENT {"type":"alarm","code":201}'

        return 'STATE {"X":1.0,"Y":2.0,"Z":3.0,"F":1200,"S":8000}'
