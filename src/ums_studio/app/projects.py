from pathlib import Path
import json
from typing import List, Dict, Any


class ProjectManager:
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.recent_file = self.data_root / "recent.json"

    def list_recent(self) -> List[str]:
        if not self.recent_file.exists():
            return []
        try:
            return json.loads(self.recent_file.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_recent(self, paths: List[str]):
        self.recent_file.write_text(json.dumps(paths, indent=2), encoding="utf-8")

    def create_project(self, name: str, machine_config: Dict[str, Any]) -> Path:
        path = self.data_root / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "program.ums").write_text("", encoding="utf-8")
        (path / "machine.json").write_text(json.dumps(machine_config, indent=2), encoding="utf-8")
        rec = self.list_recent()
        rec.insert(0, str(path))
        self._save_recent(rec[:20])
        return path

    def load_project(self, path: Path) -> Dict[str, Any]:
        program = (path / "program.ums").read_text(encoding="utf-8")
        machine = {}
        if (path / "machine.json").exists():
            machine = json.loads((path / "machine.json").read_text(encoding="utf-8"))
        return {"program": program, "machine": machine}

    def save_program(self, path: Path, text: str):
        (path / "program.ums").write_text(text, encoding="utf-8")
