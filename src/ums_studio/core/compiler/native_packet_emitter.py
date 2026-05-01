import binascii
import struct
from collections.abc import Iterable

from ..command_model import (
    ArcCommand,
    CoolantCommand,
    DwellCommand,
    MoveCommand,
    SpindleCommand,
)
from ..errors import ValidatorError


SYNC = b"\xAA\x55"

PACKET_TYPES = {
    "move": 0x01,
    "arc": 0x02,
    "dwell": 0x03,
    "spindle": 0x04,
    "coolant": 0x05,
    "system": 0x06,
}


class NativePacketEmitter:
    def __init__(self, target: str = "stm32f4"):
        if target.lower() != "stm32f4":
            raise ValueError("Native packet output currently supports only the stm32f4 target")
        self.target = target.lower()
        self.seq = 1

    def emit(self, commands: Iterable[object]) -> list[bytes]:
        return [self._emit_command(command) for command in commands]

    def _emit_command(self, command: object) -> bytes:
        if isinstance(command, MoveCommand):
            payload = {**command.axes, "rapid": int(command.rapid)}
            if command.feed_rate is not None:
                payload["F"] = command.feed_rate
            return self._encode(PACKET_TYPES["move"], payload)
        if isinstance(command, ArcCommand):
            payload = {**command.axes, **command.center_offset, "cw": int(command.clockwise)}
            if command.feed_rate is not None:
                payload["F"] = command.feed_rate
            return self._encode(PACKET_TYPES["arc"], payload)
        if isinstance(command, DwellCommand):
            return self._encode(PACKET_TYPES["dwell"], {"P": command.duration_ms})
        if isinstance(command, SpindleCommand):
            payload = {"enabled": int(command.enabled)}
            if command.speed is not None:
                payload["S"] = command.speed
            if command.direction is not None:
                payload["dir"] = command.direction
            return self._encode(PACKET_TYPES["spindle"], payload)
        if isinstance(command, CoolantCommand):
            return self._encode(
                PACKET_TYPES["coolant"],
                {"flood": int(bool(command.flood)), "mist": int(bool(command.mist))},
            )
        raise ValidatorError(f"Cannot emit unsupported command {type(command)}")

    def _encode(self, packet_type: int, payload: dict[str, object]) -> bytes:
        body = bytearray()
        for key, value in payload.items():
            key_bytes = key.encode("ascii")
            value_bytes = self._format_value(value).encode("ascii")
            if len(key_bytes) > 255 or len(value_bytes) > 255:
                raise ValidatorError("STM32F4 packet key/value exceeds 255 bytes")
            body.append(len(key_bytes))
            body.extend(key_bytes)
            body.append(len(value_bytes))
            body.extend(value_bytes)

        length = 1 + 2 + len(body) + 2
        if length > 255:
            raise ValidatorError("STM32F4 packet exceeds 255-byte protocol length")

        header = bytearray(SYNC)
        header.append(length)
        header.append(packet_type)
        header.extend(struct.pack(">H", self.seq))
        self.seq = (self.seq + 1) & 0xFFFF

        packet = header + body
        crc = binascii.crc_hqx(packet, 0xFFFF)
        packet.extend(struct.pack(">H", crc))
        return bytes(packet)

    def _format_value(self, value: object) -> str:
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return f"{value:.4f}".rstrip("0").rstrip(".")
        return str(value)
