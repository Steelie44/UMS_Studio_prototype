from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    type: str
    value: str
    line: int


class Tokenizer:
    def tokenize(self, text: str) -> List[Token]:
        tokens: List[Token] = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            line = line.split(";")[0].strip()
            if not line:
                continue
            for part in line.split():
                tokens.append(Token(type="WORD", value=part, line=lineno))
        return tokens
