import binascii
import struct
from collections.abc import Iterable

from ...transport.transport_base import TransportBase
from .native_packet_emitter import SYNC


TYPE_OK = 0x10
TYPE_ERR = 0x11


class NativePacketStreamError(RuntimeError):
    pass


class NativePacketStreamer:
    def __init__(self, transport: TransportBase, wait_for_ack: bool = True):
        self.transport = transport
        self.wait_for_ack = wait_for_ack

    def stream(self, packets: Iterable[bytes]) -> None:
        for packet in packets:
            self.transport.send_line(packet)
            if self.wait_for_ack:
                self._wait_for_ack()

    def _wait_for_ack(self) -> None:
        while True:
            response = self.transport.read_line()
            if not response:
                continue
            if isinstance(response, str):
                normalized = response.strip().lower()
                if normalized == "ok" or normalized.startswith("ok "):
                    return
                if normalized.startswith("err") or normalized.startswith("error"):
                    raise NativePacketStreamError(response)
                continue

            decoded = self._decode_packet(response)
            if decoded["type"] == TYPE_OK:
                return
            if decoded["type"] == TYPE_ERR:
                raise NativePacketStreamError(str(decoded["payload"]))

    def _decode_packet(self, packet: bytes) -> dict[str, object]:
        if not packet.startswith(SYNC) or len(packet) < 8:
            return {"type": "invalid", "payload": {}}

        packet_type = packet[3]
        seq = struct.unpack(">H", packet[4:6])[0]
        payload = packet[6:-2]
        crc_recv = struct.unpack(">H", packet[-2:])[0]
        crc_calc = binascii.crc_hqx(packet[:-2], 0xFFFF)
        if crc_recv != crc_calc:
            return {"type": "crc_error", "seq": seq, "payload": {}}

        return {"type": packet_type, "seq": seq, "payload": payload}
