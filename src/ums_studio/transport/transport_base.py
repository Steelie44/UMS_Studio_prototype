from abc import ABC, abstractmethod


class TransportBase(ABC):
    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def send_line(self, data: str | bytes) -> None:
        ...

    @abstractmethod
    def read_line(self) -> str | bytes:
        ...
