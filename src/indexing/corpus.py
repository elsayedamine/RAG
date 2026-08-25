import re
from .chunker import Chunker
from typing import List


# 'r' prevents py from interpreting special chars
# before reg engine sees them.
# but i dont need it here
TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")

class Corpus:
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

    @classmethod
    def convert_to_corpus(cls, data):
        corpus = cls.__new__(cls)
        corpus.corpus = data
        corpus.documents = [
            cls.tokenize(chunk["text"])
            for chunk in data
        ]
        return corpus

    def __init__(self, chunker: Chunker):
        self.chunker = chunker
        self.corpus = [ {"file":file["file"], **chunk}
            for file in chunker.md_chunks + chunker.py_chunks
            for chunk in file["chunks"]
        ]
        self.documents = [ self.tokenize(chunk["text"])
            for chunk in self.corpus
        ]