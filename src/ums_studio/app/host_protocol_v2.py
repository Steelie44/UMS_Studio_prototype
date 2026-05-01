from typing import Dict, Any
import struct
import binascii


SYNC = b"\xAA\x55"


class HostProtocolV2:
    def __init__(self):
        self.seq = 1

    def next_seq(self) -> int:
        s = self.seq
        self.seq += 1
        return s

    def encode(self, pkt_type: int, payload: Dict[str, Any]) -> bytes:
        seq = self.next_seq()

        body = bytearray()
        for k, v in payload.items():
            key = k.encode("ascii")
            if isinstance(v, (int, float)):
                val = str(v).encode("ascii")
            else:
                val = str(v).encode("ascii")
            body.append(len(key))
            body.extend(key)
            body.append(len(val))
            body.extend(val)

        length = 1 + 2 + len(body) + 2

        header = bytearray()
        header.extend(SYNC)
        header.append(length)
        header.append(pkt_type)
        header.extend(struct.pack(">H", seq))

        packet = header + body

        crc = binascii.crc_hqx(packet, 0xFFFF)
        packet.extend(struct.pack(">H", crc))

        return bytes(packet)

    def decode(self, data: bytes) -> Dict[str, Any]:
        if not data.startswith(SYNC):
            return {"type": "invalid"}

        length = data[2]
        pkt_type = data[3]
        seq = struct.unpack(">H", data[4:6])[0]

        body = data[6:-2]
        crc_recv = struct.unpack(">H", data[-2:])[0]
        crc_calc = binascii.crc_hqx(data[:-2], 0xFFFF)

        if crc_recv != crc_calc:
            return {"type": "crc_error"}

        pos = 0
        payload = {}

        while pos < len(body):
            klen = body[pos]
            pos += 1
            key = body[pos:pos + klen].decode("ascii")
            pos += klen
            vlen = body[pos]
            pos += 1
            val = body[pos:pos + vlen].decode("ascii")
            pos += vlen
            payload[key] = val

        return {
            "type": pkt_type,
            "seq": seq,
            "payload": payload,
        }
