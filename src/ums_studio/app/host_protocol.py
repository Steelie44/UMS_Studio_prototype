from typing import Dict, Any
from .host_protocol_v2 import HostProtocolV2


class HostProtocol:
    def __init__(self):
        self.v2 = HostProtocolV2()
        self.seq = 1
        self.use_v2 = False

    def next_seq(self) -> int:
        s = self.seq
        self.seq += 1
        return s

    def encode(self, cmd_type: str, payload: Dict[str, Any]):
        if self.use_v2:
            pkt_map = {
                "MOVE": 1,
                "ARC": 2,
                "DWELL": 3,
                "SPINDLE": 4,
                "COOLANT": 5,
                "SYSTEM": 6,
            }
            return self.v2.encode(pkt_map[cmd_type], payload)
        seq = self.next_seq()
        parts = [f"CMD {seq} {cmd_type}"]
        for k, v in payload.items():
            parts.append(f"{k}={v}")
        return " ".join(parts)

    def decode(self, data: str | bytes) -> Dict[str, Any]:
        if isinstance(data, bytes) and data.startswith(b"\xAA\x55"):
            self.use_v2 = True
            return self.v2.decode(data)

        line = data.strip()

        if line.startswith("OK"):
            _, seq, *msg = line.split(" ", 2)
            return {"type": "ok", "seq": int(seq), "message": " ".join(msg)}

        if line.startswith("ERR"):
            _, seq, code, *msg = line.split(" ", 3)
            return {
                "type": "error",
                "seq": int(seq),
                "code": int(code),
                "message": " ".join(msg),
            }

        if line.startswith("STATE"):
            _, json_str = line.split(" ", 1)
            return {"type": "state", "json": json_str}

        if line.startswith("EVENT"):
            _, json_str = line.split(" ", 1)
            return {"type": "event", "json": json_str}

        return {"type": "text", "payload": line}
