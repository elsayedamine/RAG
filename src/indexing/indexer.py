from .chunker import Chunker
from typing import List
import re

# 'r' prevents py from interpreting special chars
# before reg engine sees them.
# but i dont need it here
TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")

class Indexer:
    @staticmethod
    def tokenize(text: str) -> List[str]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        text = text.lower()
        tokens: List[str] = TOKEN_PATTERN.findall(text)
        results: List[str] = []

        for token in tokens:
            results.append(token)
            if "_" in token:
                parts = [part for part in token.split("_") if part]
                results.extend(parts)
        return results

    def __init__(self, chunker: Chunker):
        self.corpus = [ {"file":file["file"], **chunk}
            for file in chunker.md_chunks + chunker.py_chunks
            for chunk in file["chunks"]
        ]
        self.documents = [ self.tokenize(chunk["text"])
            for chunk in self.corpus
        ]

if __name__ == "__main__":
    index = Indexer(Chunker())
    print(index.documents)