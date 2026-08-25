from .chunker import Chunker
from typing import List, Dict
import re
from math import log

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

    def __init__(self, chunker: Chunker):
        self.chunker = chunker
        self.corpus = [ {"file":file["file"], **chunk}
            for file in chunker.md_chunks + chunker.py_chunks
            for chunk in file["chunks"]
        ]
        self.documents = [ self.tokenize(chunk["text"])
            for chunk in self.corpus
        ]

class Indexer:
    def term_freq_indexer(self, docs: List[List[str]]) -> Dict[str, Dict[int, int]]:
        index: Dict[str, Dict[int, int]] = {}
        for doc_id, doc in enumerate(docs):
            for token in doc:
                if token not in index:
                    index[token] = {}
                if doc_id not in index[token]:
                    index[token][doc_id] = 1
                else:
                    index[token][doc_id] += 1
        return index

    def doc_length_index(self, docs: List[List[str]]) -> Dict[int, int]:
        doc_len: Dict[int, int] = {}
        for doc_id, doc in enumerate(docs):
            doc_len[doc_id] = len(doc)
        return doc_len

    def average_doc_len(self) -> float:
        return sum(self.DL.values()) / len(self.DL)

    def df(self) -> Dict[str, int]:
        df :Dict[str, int] = {}
        terms = self.TF
        for term, docs in terms.items():
            df[term] = len(docs.values())
        return df

    def idf(self) -> Dict[str, float]:
        idf: Dict[str, float] = {}
        for token, df in self.DF.items():
            idf[token] = log((self.N - df + 0.5) / (df + 0.5) + 1)
        return idf

    def bm25_score(self, query: List[str], doc_id: int) -> float:
        k1 = 1.5
        b = .75
        score = 0
        avgdl = self.avgdl
        for token in query:
            if token not in self.IDF:
                continue
            idf = self.IDF[token]
            tf = self.TF[token].get(doc_id, 0) if token in self.TF else 0
            dl = self.DL[doc_id]
            score += idf * (tf * (k1 + 1) / (tf + k1 * (1 - b + b * (dl / avgdl))))
        return score

    def __init__(self, corpus: Corpus):
        self.corpus = corpus
        self.N = len(self.corpus.documents) # total documents
        self.TF = self.term_freq_indexer(self.corpus.documents) # term freq
        self.DL = self.doc_length_index(self.corpus.documents) # Doc Lengths
        self.avgdl = self.average_doc_len() # avrg doc len
        self.DF = self.df() # doc freq for each term
        self.IDF = self.idf()


if __name__ == "__main__":
    class TestCorpus:
        documents = [
            ["python", "socket", "server"],
            ["python", "python", "server"],
            ["socket", "programming"],
        ]

    query = ["python"]

    indexer = Indexer(TestCorpus())

    for doc_id in range(len(TestCorpus.documents)):
        print(f"doc {doc_id}: {indexer.bm25_score(query, doc_id)}")