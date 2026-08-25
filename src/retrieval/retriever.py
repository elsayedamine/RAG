from src.indexing import Indexer, Corpus
from src.indexing.chunker import Chunker
from typing import List, Dict, Set

class Retriever:
    def __init__(self, index: Indexer):
        self.index = index

    def _get_doc_candidates(self, query_tokens: List[str]) -> Set[int]:
        candidates: Set[int] = set()

        for token in query_tokens:
            if token in self.index.TF:
                candidates.update(self.index.TF[token].keys())

        return candidates

    def retrieve(self, query: str, k: int) -> List[Dict]:
        tokens = Corpus.tokenize(query)
        doc_ids = self._get_doc_candidates(tokens)
        scores = {
            doc_id: self.index.bm25_score(tokens, doc_id)
            for doc_id in doc_ids
        }
        ranked = sorted(scores.items(), key=lambda item:item[1],reverse=True)
        top_k = ranked[:k]
        results = []
        for doc_id, _ in top_k:
            chunk = self.index.corpus.corpus[doc_id]
            results.append({
                "file_path": chunk['file'],
                "first_character_index": chunk['start'],
                "last_character_index": chunk['end']
            })
        return results



if __name__ == "__main__":
    indexer = Indexer(Corpus(Chunker()))
    indexer.save("data/processed/index.json")

    indexer = Indexer.load("data/processed/index.json")
    retriever = Retriever(indexer)

    queries = [
        "How does vLLM handle LoRA?",
        "How does the retrieval system work?",
        "How are Python files chunked?"
    ]

    for query in queries:
        print(f"\nQUERY: {query}")
        results = retriever.retrieve(query, 5)

        for i, result in enumerate(results, 1):
            print(f"{i}. {result}")