from collections.abc import Iterable

from ...transport.transport_base import TransportBase
from .targets import TargetProfile, get_target


class GCodeStreamError(RuntimeError):
    pass


class GCodeStreamer:
    def __init__(self, transport: TransportBase, target: str | TargetProfile):
        self.transport = transport
        self.target = get_target(target) if isinstance(target, str) else target

    def stream(self, gcode: str | Iterable[str]) -> None:
        lines = gcode.splitlines() if isinstance(gcode, str) else gcode
        for line in lines:
            clean = line.strip()
            if not clean:
                continue
            self.transport.send_line(clean)
            if self.target.requires_line_ack:
                self._wait_for_ack(clean)

    def _wait_for_ack(self, line: str) -> None:
        while True:
            response = self.transport.read_line()
            if isinstance(response, bytes):
                response = response.decode("ascii", errors="ignore")
            normalized = response.strip().lower()
            if not normalized:
                continue
            if normalized == "ok" or normalized.startswith("ok "):
                return
            if normalized.startswith("error") or normalized.startswith("alarm"):
                raise GCodeStreamError(f"{self.target.name} rejected '{line}': {response}")
