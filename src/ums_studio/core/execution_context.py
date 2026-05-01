from dataclasses import dataclass
from typing import List, Any


@dataclass
class ExecutionContext:
    ast: List[Any]
    line_index: int = 0
