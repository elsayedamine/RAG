from .corpus import Corpus
from typing import List, Dict
import os, json
from math import log


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

    def bm25_score(self, query_tokens: list[str], doc_id: int) -> float:
            score = 0.0

            k1 = 1.5
            b = 0.55  # Reduced slightly from 0.75 to soften penalty on detailed doc sections

            # Deduplicate query tokens to eliminate sub-token overcounting
            unique_qtokens = set(query_tokens)

            for token in unique_qtokens:
                tf = self.TF.get(token, {}).get(doc_id, 0)
                if tf == 0:
                    continue

                idf = self.IDF.get(token, 0.0)

                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (self.DL[doc_id] / self.avgdl))

                score += idf * (numerator / denominator)

            # Bigram Phrase Match Boost
            if len(query_tokens) >= 2:
                doc_toks = self.corpus.documents[doc_id]
                if len(doc_toks) >= 2:
                    doc_bigrams = set(zip(doc_toks[:-1], doc_toks[1:]))
                    for i in range(len(query_tokens) - 1):
                        bigram = (query_tokens[i], query_tokens[i + 1])
                        if bigram in doc_bigrams:
                            term1_idf = self.IDF.get(query_tokens[i], 1.0)
                            term2_idf = self.IDF.get(query_tokens[i + 1], 1.0)
                            score += 0.75 * (term1_idf + term2_idf)

            return score

    def __init__(self, corpus: Corpus):
        self.corpus = corpus
        self.N = len(self.corpus.documents) # total documents
        self.TF = self.term_freq_indexer(self.corpus.documents) # term freq
        self.DL = self.doc_length_index(self.corpus.documents) # Doc Lengths
        self.avgdl = self.average_doc_len() # avrg doc len
        self.DF = self.df() # doc freq for each term
        self.IDF = self.idf()
    
    def save(self, path: str):
        data = {
            "N": self.N,
            "TF": self.TF,
            "DL": self.DL,
            "avgdl": self.avgdl,
            "DF": self.DF,
            "IDF": self.IDF,
            "corpus": self.corpus.corpus,
        }
        os.makedirs('data/processed', exist_ok=True)
        with open(path, "w") as js:
            json.dump(data, js, indent=4)

    @classmethod
    def load(cls, path: str) -> "Indexer":
        with open(path, "r") as js:
            data = json.load(js)

        indexer = cls.__new__(cls)

        indexer.N = data["N"]
        indexer.TF = {
            term: {int(doc_id): tf for doc_id, tf in docs.items()}
            for term, docs in data["TF"].items()
        }
        indexer.DL = {int(doc_id): length for doc_id, length in data["DL"].items()}
        indexer.avgdl = data["avgdl"]
        indexer.DF = data["DF"]
        indexer.IDF = data["IDF"]
        indexer.corpus = Corpus.convert_to_corpus(data["corpus"])

        return indexer


if __name__ == "__main__":
    class TestCorpus:
        documents = [
            ["python", "socket", "server"],
            ["python", "python", "server"],
            ["socket", "programming"],
        ]

        corpus = [
            {"file": "test.py", "text": "python socket server"},
            {"file": "test.py", "text": "python python server"},
            {"file": "test.py", "text": "socket programming"},
        ]

    query = ["python"]

    indexer = Indexer(TestCorpus())
    indexer.save("data/processed/index.json")
    loaded = Indexer.load("data/processed/index.json")

    # Compare
    for doc_id in range(len(TestCorpus.documents)):
        original = indexer.bm25_score(query, doc_id)
        restored = loaded.bm25_score(query, doc_id)

        print(f"doc {doc_id}:")
        print(f"  original: {original}")
        print(f"  loaded:   {restored}")