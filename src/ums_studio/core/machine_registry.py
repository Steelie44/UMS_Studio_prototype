import json
from pathlib import Path

class MachineRegistry:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(exist_ok=True)

    def list_machines(self):
        return [p.stem for p in self.root.glob("*.json")]

    def load(self, name: str):
        path = self.root / f"{name}.json"
        with open(path, "r") as f:
            return json.load(f)

    def install(self, path: Path):
        dest = self.root / path.name
        dest.write_bytes(path.read_bytes())
